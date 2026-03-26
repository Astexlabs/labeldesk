import tempfile
from pathlib import Path

from PIL import Image

from labeldesk.core.paths import expandImgPaths


def test_expandSingleFile():
    d = tempfile.mkdtemp()
    p = Path(d) / "a.png"
    Image.new("RGB", (10, 10)).save(p)
    out = expandImgPaths([str(p)])
    assert len(out) == 1


def test_expandDir():
    d = tempfile.mkdtemp()
    Image.new("RGB", (10, 10)).save(Path(d) / "a.png")
    Image.new("RGB", (10, 10)).save(Path(d) / "b.jpg")
    (Path(d) / "readme.txt").write_text("nope")
    out = expandImgPaths([d])
    assert len(out) == 2


def test_expandRecursive():
    d = Path(tempfile.mkdtemp())
    sub = d / "sub"
    sub.mkdir()
    Image.new("RGB", (10, 10)).save(d / "a.png")
    Image.new("RGB", (10, 10)).save(sub / "b.png")
    assert len(expandImgPaths([d], recursive=False)) == 1
    assert len(expandImgPaths([d], recursive=True)) == 2


def test_expandMissingPath():
    assert expandImgPaths(["/no/such/thing"]) == []
