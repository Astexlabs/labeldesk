import tempfile

from PIL import Image

from labeldesk.pipeline.normalizer import normalizeImg, compressToTarget


def test_normalizeResizes():
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", (2000, 1500)).save(f.name)
    out = normalizeImg(f.name, maxSide=768)
    img = Image.open(__import__("io").BytesIO(out))
    assert max(img.size) <= 768


def test_normalizeConvertsRgba():
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGBA", (100, 100)).save(f.name)
    out = normalizeImg(f.name)
    assert len(out) > 0


def test_compressNoChange():
    small = b"\xff" * 100
    assert compressToTarget(small, targetKb=1) == small
