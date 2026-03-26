import tempfile
from pathlib import Path

from labeldesk.core.models.result import LabelResult
from labeldesk.core.output.formatters import fmtResults, sanitizeFname


def test_sanitizeFname():
    assert sanitizeFname("Hello World!") == "hello-world"
    assert sanitizeFname("  Messy  Title  ") == "messy-title"
    assert sanitizeFname("a" * 200) == "a" * 80
    assert sanitizeFname("") == "untitled"


def test_fmtPreview():
    res = {"/tmp/a.png": LabelResult(title="cat", src="ai")}
    out = fmtResults(res, "preview")
    assert "cat" in out
    assert "a.png" in out


def test_fmtJson():
    res = {"/tmp/a.png": LabelResult(title="cat")}
    out = fmtResults(res, "json")
    assert '"cat"' in out


def test_fmtCsv():
    res = {"/tmp/a.png": LabelResult(title="cat", tags=["cute"])}
    out = fmtResults(res, "csv")
    assert "cat" in out
    assert "cute" in out


def test_fmtCsvToFile():
    res = {"/tmp/a.png": LabelResult(title="x")}
    d = Path(tempfile.mkdtemp())
    path = fmtResults(res, "csv", outDir=d)
    assert Path(path).exists()
