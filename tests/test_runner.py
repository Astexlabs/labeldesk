import tempfile
from pathlib import Path

from PIL import Image

from labeldesk.core.models.categories import ImgCat
from labeldesk.pipeline.runner import PipelineRunner, _heuristicLabel, _buildCtx
from labeldesk.pipeline.signals import FreeSignals


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
    assert _heuristicLabel(sig, ImgCat.outdoor) is None


def test_buildCtxWithInfo():
    sig = FreeSignals(camModel="Canon", aspect="landscape", brightness="high-key")
    ctx = _buildCtx(sig)
    assert "Canon" in ctx
    assert "landscape" in ctx


def test_processOneSolidImg():
    p = _mkImg(color=(255, 0, 0), sz=(64, 64))
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        runner = PipelineRunner(cachePath=db.name)
        res = runner.processOne(p)
        assert res.src == "heuristic"
        assert "ff0000" in res.title
        runner.close()


def test_processManyWithDir():
    d = tempfile.mkdtemp()
    Image.new("RGB", (64, 64), (255, 0, 0)).save(Path(d) / "a.png")
    Image.new("RGB", (64, 64), (0, 255, 0)).save(Path(d) / "b.png")
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        runner = PipelineRunner(cachePath=db.name)
        results = runner.processMany([d])
        assert len(results) == 2
        runner.close()


def test_processManyEmptyDir():
    d = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(suffix=".db") as db:
        runner = PipelineRunner(cachePath=db.name)
        results = runner.processMany([d])
        assert results == {}
        runner.close()
