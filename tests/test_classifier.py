import tempfile

from PIL import Image

from core.models.categories import ImgCat
from pipeline.classifier import LocalClassifier
from pipeline.signals import extractSignals


def _mkImg(color=(128, 128, 128), sz=(200, 200)):
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", sz, color).save(f.name)
    return f.name


def test_noModelReturnsGeneric():
    c = LocalClassifier(modelPath=None)
    p = _mkImg()
    assert c.classify(p) == ImgCat.generic


def test_signalsFallbackScreenshot():
    c = LocalClassifier()
    p = _mkImg()
    sig = extractSignals(p)
    sig.fnameHints = ["screenshot"]
    assert c.classifyFromSignals(sig) == ImgCat.screenshot


def test_signalsFallbackSolid():
    c = LocalClassifier()
    p = _mkImg(color=(255, 0, 0))
    sig = extractSignals(p)
    sig.isSolid = True
    assert c.classifyFromSignals(sig) == ImgCat.icon


def test_signalsFallbackPanorama():
    c = LocalClassifier()
    sig = extractSignals(_mkImg(sz=(3000, 500)))
    sig.isSolid = False
    sig.isMono = False
    sig.edgeDensity = 0.2
    assert c.classifyFromSignals(sig) == ImgCat.outdoor
