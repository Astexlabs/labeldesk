from labeldesk.core.models.base import ModelCfg
from labeldesk.core.models.registry import getAdapter, listAdapters


def test_listAdapters():
    names = listAdapters()
    assert "anthropic" in names
    assert "openai" in names
    assert "gemini" in names
    assert "ollama" in names


def test_getAdapter():
    a = getAdapter("ollama", ModelCfg())
    assert a.name == "ollama"


def test_unknownAdapter():
    try:
        getAdapter("nope", ModelCfg())
        assert False
    except ValueError:
        pass
