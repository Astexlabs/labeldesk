import tempfile

from PIL import Image

from pipeline.signals import extractSignals, _classifyAspect, _classifyBrightness, _checkSolid


def _mkImg(color=(128, 128, 128), sz=(200, 200)):
    img = Image.new("RGB", sz, color)
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(f.name)
    return f.name


def test_aspectClassification():
    assert _classifyAspect(1920, 1080) == "landscape"
    assert _classifyAspect(1080, 1920) == "portrait"
    assert _classifyAspect(1000, 1000) == "square"
    assert _classifyAspect(5000, 1000) == "panoramic"


def test_solidDetected():
    img = Image.new("RGB", (64, 64), (255, 0, 0))
    assert _checkSolid(img) is True


def test_nonSolid():
    img = Image.new("RGB", (64, 64))
    for x in range(64):
        for y in range(64):
            img.putpixel((x, y), (x * 4, y * 4, 128))
    assert _checkSolid(img) is False


def test_extractSignalsBasic():
    p = _mkImg(color=(200, 200, 200), sz=(300, 200))
    sig = extractSignals(p)
    assert sig.width == 300
    assert sig.height == 200
    assert sig.aspect == "landscape"
    assert sig.isSolid is True


def test_brightnessClassification():
    bright = Image.new("RGB", (64, 64), (240, 240, 240))
    assert _classifyBrightness(bright) == "high-key"
    dark = Image.new("RGB", (64, 64), (20, 20, 20))
    assert _classifyBrightness(dark) == "dark"
