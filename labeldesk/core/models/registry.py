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


_meta = {
    "anthropic": {"default": "claude-haiku-4-5-20251001", "needs": "api_key",
                  "desc": "fast + cheap vision, great default"},
    "openai": {"default": "gpt-4o-mini", "needs": "api_key",
               "desc": "solid vision, wide compat"},
    "gemini": {"default": "gemini-1.5-flash", "needs": "api_key",
               "desc": "cheapest cloud option"},
    "ollama": {"default": "llava", "needs": "host",
               "desc": "runs on ur box, free, needs gpu"},
}


def adapterInfo(name: str) -> dict:
    cls = _reg.get(name)
    m = _meta.get(name, {})
    return {
        "name": name,
        "displayName": getattr(cls, "displayName", name) if cls else name,
        "defaultModelId": m.get("default", ""),
        "desc": m.get("desc", ""),
        "needs": m.get("needs", "api_key"),
        "costPer1kIn": getattr(cls, "costPer1kIn", 0.0) if cls else 0.0,
    }


def _autoload():
    from labeldesk.core.models import anthropic_adapter, openai_adapter, gemini_adapter, ollama_adapter  # noqa


_autoload()
