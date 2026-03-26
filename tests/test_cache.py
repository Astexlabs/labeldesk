import tempfile
from pathlib import Path

from core.models.result import LabelResult
from pipeline.cache import ResultCache


def test_putAndGet():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        res = LabelResult(title="test img", desc="cool pic", tags=["a", "b"], src="vision")
        c.put("abc123", "title", "gpt4", res)
        got = c.get("abc123", "title", "gpt4")
        assert got is not None
        assert got.title == "test img"
        assert got.tags == ["a", "b"]
        assert got.cached is True
        c.close()


def test_getMiss():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        got = c.get("nope", "title", "gpt4")
        assert got is None
        c.close()


def test_getPartial():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        c.put("h1", "title", "m1", LabelResult(title="hi", src="v"))
        c.put("h1", "description", "m1", LabelResult(desc="hey", src="v"))
        parts = c.getPartial("h1", "m1")
        assert "title" in parts
        assert "description" in parts
        assert parts["title"].title == "hi"
        c.close()


def test_overwrite():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        c = ResultCache(dbPath=f.name)
        c.put("h", "t", "m", LabelResult(title="old", src="v"))
        c.put("h", "t", "m", LabelResult(title="new", src="v"))
        got = c.get("h", "t", "m")
        assert got.title == "new"
        c.close()
