import tempfile

from PIL import Image

from labeldesk.pipeline.hasher import ImgHasher


def _mkImg(color=(128, 128, 128)):
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    Image.new("RGB", (100, 100), color).save(f.name)
    return f.name


def test_computeHash():
    h = ImgHasher()
    p = _mkImg()
    assert len(h.computeHash(p)) == 16


def test_exactDupes():
    h = ImgHasher()
    p1 = _mkImg(color=(100, 100, 100))
    p2 = _mkImg(color=(100, 100, 100))
    h.findDupes(p1)
    res = h.findDupes(p2)
    assert len(res.exactDupes) == 1


def test_noDupesForDiff():
    h = ImgHasher()
    p1 = _mkImg(color=(0, 0, 0))
    h.findDupes(p1)
    p2 = _mkImg(color=(255, 255, 255))
    res = h.findDupes(p2)
    assert len(res.exactDupes) == 0
