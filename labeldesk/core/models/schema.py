from dataclasses import dataclass, field


@dataclass
class FieldSpec:
    key: str
    prompt: str
    kind: str = "str"
    toks: int = 40


_FIELDS: dict[str, FieldSpec] = {
    "title": FieldSpec("title", "short descriptive title (3-6 words)", toks=30),
    "desc": FieldSpec("desc", "one-sentence description of the image content", toks=80),
    "tags": FieldSpec("tags", "5-10 lowercase keyword tags, comma-separated", "list", 50),
    "dominant_colors": FieldSpec("dominant_colors", "3-5 dominant color names, comma-separated", "list", 30),
    "content_type": FieldSpec("content_type", "one of: photo, screenshot, diagram, icon, illustration, document, ui, meme", toks=10),
    "use_case": FieldSpec("use_case", "inferred intended use: e.g. hero-image, thumbnail, avatar, documentation, social-post, product-shot", toks=20),
    "quality_score": FieldSpec("quality_score", "image quality 1-10 (sharpness, lighting, composition), just the number", "int", 5),
    "suggested_fname": FieldSpec("suggested_fname", "a clean kebab-case filename without extension", toks=20),
    "ocr_text": FieldSpec("ocr_text", "any readable text visible in the image, or 'none'", toks=100),
    "objects": FieldSpec("objects", "main objects/subjects detected, comma-separated", "list", 50),
    "scene": FieldSpec("scene", "scene context: indoor/outdoor/studio/abstract + brief setting", toks=30),
    "confidence": FieldSpec("confidence", "your confidence in these labels 0.0-1.0, just the number", "float", 5),
}

PRESETS = {
    "basic": ["title", "desc"],
    "dataset": ["title", "tags", "content_type", "objects", "quality_score", "confidence"],
    "rename": ["suggested_fname", "content_type"],
    "full": list(_FIELDS.keys()),
}


def allFields() -> list[str]:
    return list(_FIELDS.keys())


def getSpec(key: str) -> FieldSpec | None:
    return _FIELDS.get(key)


def resolveFields(spec: str | list[str]) -> list[str]:
    """accept preset name, comma str, or list -> validated field keys"""
    if isinstance(spec, str):
        if spec in PRESETS:
            return PRESETS[spec]
        spec = [s.strip() for s in spec.split(",") if s.strip()]
    return [f for f in spec if f in _FIELDS]


def buildPrompt(fields: list[str], ctx: str = "") -> tuple[str, int]:
    """build a json-extraction prompt + token budget for the chosen fields"""
    specs = [_FIELDS[f] for f in fields if f in _FIELDS]
    if not specs:
        specs = [_FIELDS["title"]]
    lines = [f'  "{s.key}": <{s.prompt}>' for s in specs]
    body = "{\n" + ",\n".join(lines) + "\n}"
    pre = f"{ctx}. " if ctx else ""
    prompt = (f"{pre}analyze this image and return ONLY valid json "
              f"matching this schema (no markdown, no preamble):\n{body}")
    budget = sum(s.toks for s in specs) + 30
    return prompt, budget


def parseResp(raw: str, fields: list[str]) -> dict:
    """best-effort json extract + coerce types"""
    import json
    import re
    txt = raw.strip()
    m = re.search(r"\{.*\}", txt, re.DOTALL)
    if m:
        txt = m.group(0)
    try:
        data = json.loads(txt)
    except Exception:
        return {"title": raw.strip()[:100]}
    out = {}
    for f in fields:
        spec = _FIELDS.get(f)
        if not spec or f not in data:
            continue
        v = data[f]
        if spec.kind == "list" and isinstance(v, str):
            v = [x.strip() for x in v.split(",") if x.strip()]
        elif spec.kind == "int":
            try:
                v = int(float(str(v).strip()))
            except Exception:
                v = 0
        elif spec.kind == "float":
            try:
                v = float(str(v).strip())
            except Exception:
                v = 0.0
        out[f] = v
    return out
