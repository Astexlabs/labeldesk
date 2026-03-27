from labeldesk.core.models.result import LabelResult


def test_merge():
    a = LabelResult(title="t", src="a")
    b = LabelResult(desc="d", src="b")
    m = a.merge(b)
    assert m.title == "t"
    assert m.desc == "d"
    assert "a" in m.src and "b" in m.src


def test_asDict():
    r = LabelResult(title="x", tags=["y"])
    d = r.asDict()
    assert d["title"] == "x"
    assert d["tags"] == ["y"]


def test_extraMerge():
    a = LabelResult(title="t", extra={"quality_score": 8})
    b = LabelResult(extra={"objects": ["cat"], "quality_score": 3})
    m = a.merge(b)
    assert m.extra["quality_score"] == 8
    assert m.extra["objects"] == ["cat"]


def test_getField():
    r = LabelResult(title="t", extra={"scene": "outdoor"})
    assert r.get("title") == "t"
    assert r.get("scene") == "outdoor"
    assert r.get("nope", "x") == "x"
