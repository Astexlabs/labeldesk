from labeldesk.core.models.schema import (
    allFields, getSpec, resolveFields, buildPrompt, parseResp, PRESETS,
)
from labeldesk.core.models.result import LabelResult


def test_allFields():
    f = allFields()
    assert "title" in f
    assert "quality_score" in f
    assert "objects" in f
    assert "confidence" in f


def test_getSpec():
    s = getSpec("tags")
    assert s.kind == "list"
    s = getSpec("quality_score")
    assert s.kind == "int"
    assert getSpec("nope") is None


def test_resolvePreset():
    assert resolveFields("basic") == ["title", "desc"]
    assert "quality_score" in resolveFields("dataset")
    assert len(resolveFields("full")) == len(allFields())


def test_resolveCsv():
    r = resolveFields("title, tags, bogus")
    assert r == ["title", "tags"]


def test_resolveList():
    r = resolveFields(["objects", "scene", "nah"])
    assert r == ["objects", "scene"]


def test_buildPrompt():
    p, toks = buildPrompt(["title", "tags"])
    assert "title" in p
    assert "tags" in p
    assert "json" in p.lower()
    assert toks > 50


def test_buildPromptCtx():
    p, _ = buildPrompt(["title"], ctx="product shots")
    assert "product shots" in p


def test_parseResp():
    raw = '{"title": "red car", "tags": "car, red, vehicle", "quality_score": "8"}'
    d = parseResp(raw, ["title", "tags", "quality_score"])
    assert d["title"] == "red car"
    assert d["tags"] == ["car", "red", "vehicle"]
    assert d["quality_score"] == 8


def test_parseRespMarkdown():
    raw = '```json\n{"title": "x", "confidence": 0.9}\n```'
    d = parseResp(raw, ["title", "confidence"])
    assert d["title"] == "x"
    assert d["confidence"] == 0.9


def test_parseRespBad():
    d = parseResp("not json at all", ["title"])
    assert "title" in d


def test_fromFields():
    r = LabelResult.fromFields({
        "title": "t", "tags": ["a"], "quality_score": 7, "objects": ["cat"],
    })
    assert r.title == "t"
    assert r.tags == ["a"]
    assert r.extra["quality_score"] == 7
    assert r.get("objects") == ["cat"]
    d = r.asDict()
    assert d["quality_score"] == 7


def test_fromFieldsFnameFallback():
    r = LabelResult.fromFields({"suggested_fname": "my-pic"})
    assert r.title == "my-pic"


def test_presetsValid():
    for name, flds in PRESETS.items():
        for f in flds:
            assert getSpec(f) is not None, f"preset {name} has bad field {f}"
