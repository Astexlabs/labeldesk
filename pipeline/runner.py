from pathlib import Path

from core.models.categories import ImgCat
from core.models.result import LabelResult
from core.models.text_adapter_mixin import TxtAdapterMixin
from pipeline.batcher import BatchItem, buildBatches, budgetFor
from pipeline.cache import ResultCache
from pipeline.classifier import LocalClassifier
from pipeline.hasher import ImgHasher
from pipeline.ocr import extractTxt, summarizeTxt
from pipeline.signals import FreeSignals, extractSignals


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
        adapter: TxtAdapterMixin | None = None,
        modelName: str = "default",
        mode: str = "title",
        onnxPath: str | None = None,
        cachePath: str = ".labeldesk_cache.db",
        batchSz: int = 5,
        collectionCtx: str = "",
    ):
        self._adapter = adapter
        self._model = modelName
        self._mode = mode
        self._hasher = ImgHasher()
        self._classifier = LocalClassifier(modelPath=onnxPath)
        self._cache = ResultCache(dbPath=cachePath)
        self._batchSz = batchSz
        self._collectionCtx = collectionCtx

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

        if self._classifier._session:
            cat = self._classifier.classify(p)
        else:
            cat = self._classifier.classifyFromSignals(signals)

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

    def processMany(self, imgPaths: list[str | Path]) -> dict[str, LabelResult]:
        """batch pipeline for multiple imgs"""
        results: dict[str, LabelResult] = {}
        needsAi: list[tuple[str, str, ImgCat, FreeSignals]] = []

        for imgPath in imgPaths:
            p = Path(imgPath)
            signals = extractSignals(p)
            hashRes = self._hasher.findDupes(p)
            key = str(p)

            cached = self._cache.get(hashRes.phash, self._mode, self._model)
            if cached:
                results[key] = cached
                continue

            if self._classifier._session:
                cat = self._classifier.classify(p)
            else:
                cat = self._classifier.classifyFromSignals(signals)

            heur = _heuristicLabel(signals, cat)
            if heur:
                self._cache.put(hashRes.phash, self._mode, self._model, heur)
                results[key] = heur
                continue

            if cat in (ImgCat.screenshot, ImgCat.document, ImgCat.diagram):
                res = self._ocrPath(p, hashRes.phash, signals)
                results[key] = res
                continue

            needsAi.append((key, hashRes.phash, cat, signals))

        if needsAi and self._adapter:
            batchItems = [
                BatchItem(imgPath=k, cat=cat, ctx=_buildCtx(sig))
                for k, _ph, cat, sig in needsAi
            ]
            batches = buildBatches(batchItems, batchSz=self._batchSz)
            for batch in batches:
                for item in batch.items:
                    res = self._visionPath(
                        item.imgPath,
                        dict(needsAi)[item.imgPath]
                        if False
                        else next(
                            ph for k, ph, c, s in needsAi if k == item.imgPath
                        ),
                        batch.cat,
                        next(s for k, ph, c, s in needsAi if k == item.imgPath),
                    )
                    results[item.imgPath] = res

        return results

    def _ocrPath(
        self, imgPath: Path, phash: str, signals: FreeSignals
    ) -> LabelResult:
        raw = extractTxt(imgPath)
        summary = summarizeTxt(raw)
        if not summary:
            return self._visionPath(
                imgPath,
                phash,
                ImgCat.generic,
                signals,
            )
        if self._adapter and self._adapter.canTxt():
            prompt = f"give a short title for this content: {summary}"
            title = self._adapter.txtInfer(summary, prompt, maxToks=60)
            res = LabelResult(title=title.strip(), src="ocr+txt-llm")
        else:
            words = summary.split()[:8]
            title = " ".join(words)
            res = LabelResult(title=title, src="ocr-only")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def _visionPath(
        self,
        imgPath: str | Path,
        phash: str,
        cat: ImgCat,
        signals: FreeSignals,
    ) -> LabelResult:
        if not self._adapter:
            return LabelResult(title="no-adapter", src="none")
        budget = budgetFor(cat)
        ctx = _buildCtx(signals)
        ctxLine = ""
        if self._collectionCtx:
            ctxLine = f"collection context: {self._collectionCtx}. "
        if ctx:
            ctxLine += f"image info: {ctx}. "

        prompt = f"{ctxLine}label this {cat.value} image."
        maxToks = sum(budget.values())

        imgBytes = Path(imgPath).read_bytes()
        raw = self._adapter.visionInfer(imgBytes, prompt, maxToks=maxToks)
        res = LabelResult(title=raw.strip(), src=f"vision-{cat.value}")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def _deltaInfer(
        self, imgPath: Path, phash: str, titleRes: LabelResult
    ) -> LabelResult:
        if not self._adapter or not self._adapter.canTxt():
            return LabelResult(src="no-txt-adapter")
        prompt = f"given title '{titleRes.title}', write a one-sentence description."
        desc = self._adapter.txtInfer("", prompt, maxToks=120)
        res = LabelResult(title=titleRes.title, desc=desc.strip(), src="delta-txt")
        self._cache.put(phash, self._mode, self._model, res)
        return res

    def close(self):
        self._cache.close()
