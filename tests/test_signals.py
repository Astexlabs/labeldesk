import tempfile

from PIL import Image

from labeldesk.pipeline.signals import (
    extractSignals, _classifyAspect, _classifyBrightness,
)


def _mkImg(color=(128, 128, 128), sz=(200, 200)):
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", sz, color).save(f.name)
    return f.name


def test_aspectRatios():
    assert _classifyAspect(300, 100) == "panoramic"
    assert _classifyAspect(200, 100) == "landscape"
    assert _classifyAspect(100, 100) == "square"
    assert _classifyAspect(100, 200) == "portrait"


def test_brightness():
    white = Image.new("RGB", (10, 10), (255, 255, 255))
    assert _classifyBrightness(white) == "high-key"
    black = Image.new("RGB", (10, 10), (0, 0, 0))
    assert _classifyBrightness(black) == "silhouette"


def test_extractSignalsSolid():
    p = _mkImg(color=(255, 0, 0))
    sig = extractSignals(p)
    assert sig.isSolid
    assert sig.dominant[0] > 200


def test_extractSignalsAspect():
    p = _mkImg(sz=(400, 100))
    sig = extractSignals(p)
    assert sig.aspect == "panoramic"
