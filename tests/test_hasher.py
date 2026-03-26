import tempfile
from pathlib import Path

from PIL import Image

from pipeline.hasher import ImgHasher


def _mkImg(color=(255, 0, 0), sz=(64, 64)):
    img = Image.new("RGB", sz, color)
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(f.name)
    return f.name


def test_sameImgSameHash():
    h = ImgHasher()
    p = _mkImg()
    h1 = h.computeHash(p)
    h2 = h.computeHash(p)
    assert h1 == h2


def test_exactDupeDetected():
    h = ImgHasher()
    p1 = _mkImg(color=(100, 100, 100))
    p2 = _mkImg(color=(100, 100, 100))
    r1 = h.findDupes(p1)
    assert r1.exactDupes == []
    r2 = h.findDupes(p2)
    assert len(r2.exactDupes) > 0


def _mkPatternImg(seed=0, sz=(64, 64)):
    import random
    random.seed(seed)
    img = Image.new("RGB", sz)
    for x in range(sz[0]):
        for y in range(sz[1]):
            img.putpixel((x, y), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(f.name)
    return f.name


def test_differentImgsNoDupe():
    h = ImgHasher()
    p1 = _mkPatternImg(seed=42)
    p2 = _mkPatternImg(seed=999)
    h.findDupes(p1)
    r2 = h.findDupes(p2)
    assert r2.exactDupes == []
