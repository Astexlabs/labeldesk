from labeldesk.core.models.base import BaseAdapter, ModelCfg

_reg: dict[str, type[BaseAdapter]] = {}


def register(name: str):
    def deco(cls):
        _reg[name] = cls
        return cls
    return deco


def getAdapter(name: str, cfg: ModelCfg) -> BaseAdapter:
    if name not in _reg:
        raise ValueError(f"no adapter '{name}', have: {list(_reg)}")
    return _reg[name](cfg)


def listAdapters() -> list[str]:
    return list(_reg.keys())


_K = lambda h: {"key": "api_key", "label": "API key", "secret": True, "hint": h}
_H = lambda h, d="": {"key": "host", "label": "Endpoint URL", "secret": False, "hint": h, "default": d}

_meta = {
    "anthropic": {"desc": "fast + cheap vision, great default",
                  "creds": [_K("get one at console.anthropic.com")],
                  "models": ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-6"]},
    "openai": {"desc": "solid vision, wide compat",
               "creds": [_K("get one at platform.openai.com")],
               "models": ["gpt-4o-mini", "gpt-4o"]},
    "gemini": {"desc": "cheapest cloud option",
               "creds": [_K("get one at aistudio.google.com")],
               "models": ["gemini-1.5-flash", "gemini-1.5-pro"]},
    "groq": {"desc": "blazing fast lpu inference, very cheap",
             "creds": [_K("free tier at console.groq.com")],
             "models": ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]},
    "lightning": {"desc": "self-hosted openai-compat endpoint on lightning studios",
                  "creds": [_H("ur lightning studio url, e.g. https://xxx.cloudspaces.litng.ai"),
                            _K("from the lightning dashboard")],
                  "models": ["lightning-vision"]},
    "ollama": {"desc": "runs on ur box, free, needs gpu",
               "creds": [_H("where ollama is running", "http://localhost:11434")],
               "models": ["llava", "llava:13b", "bakllava", "moondream"]},
}


def adapterInfo(name: str) -> dict:
    cls = _reg.get(name)
    m = _meta.get(name, {})
    creds = m.get("creds", [_K("")])
    models = m.get("models", [])
    return {
        "name": name,
        "displayName": getattr(cls, "displayName", name) if cls else name,
        "desc": m.get("desc", ""),
        "creds": creds,
        "needs": creds[0]["key"] if creds else "api_key",
        "models": models,
        "defaultModelId": models[0] if models else "",
        "costPer1kIn": getattr(cls, "costPer1kIn", 0.0) if cls else 0.0,
    }


def listProviders() -> list[dict]:
    return [adapterInfo(n) for n in _reg]


def _autoload():
    from labeldesk.core.models import (  # noqa
        anthropic_adapter, openai_adapter, gemini_adapter,
        groq_adapter, lightning_adapter, ollama_adapter,
    )


_autoload()
