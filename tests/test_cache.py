import tempfile

from labeldesk.core.models.result import LabelResult
from labeldesk.pipeline.cache import ResultCache


def test_putGet():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        r = LabelResult(title="hi", src="test")
        c.put("abc", "title", "m1", r)
        got = c.get("abc", "title", "m1")
        assert got.title == "hi"
        assert got.cached
        c.close()


def test_missReturnsNone():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        assert c.get("nope", "title", "m1") is None
        c.close()


def test_getPartial():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        c.put("xyz", "title", "m1", LabelResult(title="t"))
        c.put("xyz", "description", "m1", LabelResult(desc="d"))
        parts = c.getPartial("xyz", "m1")
        assert "title" in parts
        assert "description" in parts
        c.close()


def test_clear():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        c.put("a", "title", "m", LabelResult(title="x"))
        c.clear()
        assert c.get("a", "title", "m") is None
        c.close()
