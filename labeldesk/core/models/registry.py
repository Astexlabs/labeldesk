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


def _autoload():
    from labeldesk.core.models import anthropic_adapter, openai_adapter, gemini_adapter, ollama_adapter  # noqa


_autoload()
