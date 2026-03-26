from core.models.result import LabelResult


def test_defaultResult():
    r = LabelResult()
    assert r.title == ""
    assert r.desc == ""
    assert r.tags == []
    assert r.cached is False


def test_merge():
    a = LabelResult(title="hello", src="a")
    b = LabelResult(desc="world", tags=["x"], src="b")
    m = a.merge(b)
    assert m.title == "hello"
    assert m.desc == "world"
    assert m.tags == ["x"]
    assert "a" in m.src and "b" in m.src


def test_mergePrefersSelf():
    a = LabelResult(title="first", desc="d1", src="a")
    b = LabelResult(title="second", desc="d2", src="b")
    m = a.merge(b)
    assert m.title == "first"
    assert m.desc == "d1"
