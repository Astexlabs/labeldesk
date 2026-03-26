import tempfile
from pathlib import Path

from PIL import Image

from core.models.categories import ImgCat
from core.models.result import LabelResult
from pipeline.runner import PipelineRunner, _heuristicLabel, _buildCtx
from pipeline.signals import FreeSignals


def _mkImg(color=(128, 128, 128), sz=(200, 200)):
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", sz, color).save(f.name)
    return f.name


def test_heuristicLabelSolid():
    sig = FreeSignals(isSolid=True, dominant=(255, 0, 0), aspect="square")
    res = _heuristicLabel(sig, ImgCat.icon)
    assert res is not None
    assert "ff0000" in res.title
    assert res.src == "heuristic"


def test_heuristicLabelNonSolid():
    sig = FreeSignals(isSolid=False)
    res = _heuristicLabel(sig, ImgCat.outdoor)
    assert res is None


def test_buildCtxWithInfo():
    sig = FreeSignals(camModel="Canon", aspect="landscape", brightness="high-key")
    ctx = _buildCtx(sig)
    assert "Canon" in ctx
    assert "landscape" in ctx
    assert "high-key" in ctx


def test_buildCtxEmpty():
    sig = FreeSignals()
    ctx = _buildCtx(sig)
    assert ctx == ""


def test_processOneSolidImg():
    p = _mkImg(color=(255, 0, 0), sz=(64, 64))
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        runner = PipelineRunner(cachePath=db.name)
        res = runner.processOne(p)
        assert res.src == "heuristic"
        assert "ff0000" in res.title
        runner.close()


def test_processManyWithDupes():
    p1 = _mkImg(color=(0, 255, 0), sz=(64, 64))
    p2 = _mkImg(color=(0, 255, 0), sz=(64, 64))
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        runner = PipelineRunner(cachePath=db.name)
        results = runner.processMany([p1, p2])
        assert len(results) == 2
        runner.close()
