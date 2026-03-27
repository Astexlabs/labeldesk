from pathlib import Path

from labeldesk.core.models.categories import ImgCat
from labeldesk.core.models.result import LabelResult
from labeldesk.core.models.base import BaseAdapter
from labeldesk.core.models.schema import resolveFields, buildPrompt, parseResp
from labeldesk.core.paths import expandImgPaths, cacheDbPath
from labeldesk.pipeline.batcher import BatchItem, buildBatches, budgetFor
from labeldesk.pipeline.cache import ResultCache
from labeldesk.pipeline.classifier import LocalClassifier
from labeldesk.pipeline.hasher import ImgHasher
from labeldesk.pipeline.normalizer import normalizeImg
from labeldesk.pipeline.ocr import extractTxt, summarizeTxt
from labeldesk.pipeline.signals import FreeSignals, extractSignals


def _heuristicLabel(signals: FreeSignals, cat: ImgCat) -> LabelResult | None:
    if cat == ImgCat.icon or signals.isSolid:
        r, g, b = signals.dominant
        title = f"solid-{signals.aspect}-{r:02x}{g:02x}{b:02x}"
        return LabelResult(title=title, src="heuristic")
    return None


def _buildCtx(signals: FreeSignals) -> str:
    parts = []
    if signals.camModel:
        parts.append(f"cam:{signals.camModel}")
    if signals.focalLen:
        parts.append(f"focal:{signals.focalLen}")
    if signals.aspect != "unknown":
        parts.append(signals.aspect)
    if signals.brightness != "mid":
        parts.append(signals.brightness)
    if signals.folderHints:
        parts.append(f"folder:{'/'.join(signals.folderHints)}")
    return ", ".join(parts)


class PipelineRunner:
    """the big cascading decision tree"""

    def __init__(
        self,
        adapter: BaseAdapter | None = None,
        modelName: str = "default",
        mode: str = "title",
        onnxPath: str | None = None,
        cachePath: str | None = None,
        batchSz: int = 5,
        collectionCtx: str = "",
        fields: str | list[str] | None = None,
        progressCb=None,
    ):
        self._adapter = adapter
        self._model = modelName
        self._mode = mode
        self._fields = resolveFields(fields) if fields else []
        self._hasher = ImgHasher()
        self._classifier = LocalClassifier(modelPath=onnxPath)
        self._cache = ResultCache(dbPath=cachePath or cacheDbPath())
        self._batchSz = batchSz
        self._collectionCtx = collectionCtx
        self._progressCb = progressCb

    def _tick(self, msg: str, done: int, total: int):
        if self._progressCb:
            self._progressCb(msg, done, total)

    def processOne(self, imgPath: str | Path) -> LabelResult:
        """full pipeline for a single img"""
        p = Path(imgPath)
        signals = extractSignals(p)
        hashRes = self._hasher.findDupes(p)

        cached = self._cache.get(hashRes.phash, self._mode, self._model)
        if cached:
            return cached

        if hashRes.exactDupes:
            dupeHash = self._hasher.computeHash(hashRes.exactDupes[0])
            cached = self._cache.get(dupeHash, self._mode, self._model)
            if cached:
                self._cache.put(hashRes.phash, self._mode, self._model, cached)
                return cached

        cat = (self._classifier.classify(p) if self._classifier._session
               else self._classifier.classifyFromSignals(signals))

        heur = _heuristicLabel(signals, cat)
        if heur:
            self._cache.put(hashRes.phash, self._mode, self._model, heur)
            return heur

        if cat in (ImgCat.screenshot, ImgCat.document, ImgCat.diagram):
            return self._ocrPath(p, hashRes.phash, signals)

        if self._mode != "title":
            partial = self._cache.getPartial(hashRes.phash, self._model)
            if "title" in partial and self._mode == "description":
                return self._deltaInfer(p, hashRes.phash, partial["title"])

        return self._visionPath(p, hashRes.phash, cat, signals)

    def processMany(self, inputs: list[str | Path], recursive: bool = False) -> dict[str, LabelResult]:
        """batch pipeline - accepts files OR dirs, expands em"""
        imgPaths = expandImgPaths(inputs, recursive=recursive)
        if not imgPaths:
            return {}

        results: dict[str, LabelResult] = {}
        needsAi: list[tuple[str, str, ImgCat, FreeSignals]] = []
        total = len(imgPaths)

        for i, p in enumerate(imgPaths):
            key = str(p)
            try:
                signals = extractSignals(p)
            except Exception as e:
                results[key] = LabelResult(title=f"err: {e}", src="error")
                self._tick("skip (bad img)", i + 1, total)
                continue

            cat = (self._classifier.classify(p) if self._classifier._session
                   else self._classifier.classifyFromSignals(signals))

            heur = _heuristicLabel(signals, cat)
            if heur:
                results[key] = heur
                self._tick("heuristic", i + 1, total)
                continue

            try:
                hashRes = self._hasher.findDupes(p)
            except Exception as e:
                results[key] = LabelResult(title=f"err: {e}", src="error")
                continue

            cached = self._cache.get(hashRes.phash, self._mode, self._model)
            if cached:
                results[key] = cached
                self._tick("cache hit", i + 1, total)
                continue

            if cat in (ImgCat.screenshot, ImgCat.document, ImgCat.diagram):
                results[key] = self._ocrPath(p, hashRes.phash, signals)
                self._tick("ocr", i + 1, total)
                continue

            needsAi.append((key, hashRes.phash, cat, signals))

        if needsAi:
            lookup = {k: (ph, c, s) for k, ph, c, s in needsAi}
            if self._adapter:
                batchItems = [BatchItem(imgPath=k, cat=c, ctx=_buildCtx(s))
                              for k, ph, c, s in needsAi]
                batches = buildBatches(batchItems, batchSz=self._batchSz)
                done = total - len(needsAi)
                for batch in batches:
                    for item in batch.items:
                        ph, _c, s = lookup[item.imgPath]
                        results[item.imgPath] = self._visionPath(
                            item.imgPath, ph, batch.cat, s
                        )
                        done += 1
                        self._tick(f"ai ({batch.cat.value})", done, total)
            else:
                for k, ph, c, s in needsAi:
                    results[k] = LabelResult(title="no-adapter", src="none")

        return results

    def _ocrPath(self, imgPath: Path, phash: str, signals: FreeSignals) -> LabelResult:
        raw = extractTxt(imgPath)
        summary = summarizeTxt(raw)
        if not summary:
            return self._visionPath(imgPath, phash, ImgCat.generic, signals)
        if self._adapter and self._adapter.canTxt():
            prompt = f"give a short title for this content: {summary}"
            title = self._adapter.txtInfer(summary, prompt, maxToks=60)
            res = LabelResult(title=title.strip(), src="ocr+txt-llm")
        else:
            words = summary.split()[:8]
            res = LabelResult(title=" ".join(words), src="ocr-only")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def _visionPath(self, imgPath: str | Path, phash: str, cat: ImgCat, signals: FreeSignals) -> LabelResult:
        if not self._adapter:
            return LabelResult(title="no-adapter", src="none")
        ctx = _buildCtx(signals)
        ctxLine = ""
        if self._collectionCtx:
            ctxLine = f"collection context: {self._collectionCtx}. "
        if ctx:
            ctxLine += f"image info: {ctx}. "

        imgBytes = normalizeImg(imgPath)
        try:
            if self._fields:
                prompt, maxToks = buildPrompt(self._fields, ctxLine.rstrip(". "))
                raw = self._adapter.visionInfer(imgBytes, prompt, maxToks=maxToks)
                data = parseResp(raw, self._fields)
                res = LabelResult.fromFields(data, src=f"vision-{cat.value}")
            else:
                budget = budgetFor(cat)
                prompt = f"{ctxLine}give a short {self._mode} for this {cat.value} image. no preamble."
                mk = self._mode[:4] if self._mode.startswith("desc") else self._mode
                maxToks = budget.get(mk, 100)
                raw = self._adapter.visionInfer(imgBytes, prompt, maxToks=maxToks)
                res = LabelResult(title=raw.strip(), src=f"vision-{cat.value}")
        except Exception as e:
            res = LabelResult(title=f"err: {e}", src="error")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def _deltaInfer(self, imgPath: Path, phash: str, titleRes: LabelResult) -> LabelResult:
        if not self._adapter or not self._adapter.canTxt():
            return LabelResult(src="no-txt-adapter")
        prompt = f"given title '{titleRes.title}', write a one-sentence description."
        desc = self._adapter.txtInfer("", prompt, maxToks=120)
        res = LabelResult(title=titleRes.title, desc=desc.strip(), src="delta-txt")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def close(self):
        self._cache.close()
