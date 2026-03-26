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
