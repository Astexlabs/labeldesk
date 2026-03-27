from labeldesk.core.models.base import ModelCfg
from labeldesk.core.models.registry import getAdapter, listAdapters, adapterInfo


def test_listAdapters():
    names = listAdapters()
    for n in ["anthropic", "openai", "gemini", "groq", "lightning", "ollama"]:
        assert n in names


def test_getAdapter():
    a = getAdapter("ollama", ModelCfg())
    assert a.name == "ollama"


def test_unknownAdapter():
    try:
        getAdapter("nope", ModelCfg())
        assert False
    except ValueError:
        pass


def test_adapterInfoShape():
    info = adapterInfo("anthropic")
    assert info["name"] == "anthropic"
    assert "Claude" in info["displayName"]
    assert info["defaultModelId"]
    assert info["needs"] == "api_key"
    assert info["desc"]
    assert info["costPer1kIn"] > 0


def test_adapterInfoOllama():
    info = adapterInfo("ollama")
    assert info["needs"] == "host"
    assert info["defaultModelId"] == "llava"
    assert info["costPer1kIn"] == 0.0


def test_adapterInfoUnknown():
    info = adapterInfo("nope")
    assert info["name"] == "nope"
    assert info["displayName"] == "nope"
    assert info["defaultModelId"] == ""


def test_groqAdapter():
    a = getAdapter("groq", ModelCfg(apiKey="gsk_x"))
    assert a.name == "groq"
    assert a.isAvail()
    assert not getAdapter("groq", ModelCfg()).isAvail()
    info = adapterInfo("groq")
    assert "Groq" in info["displayName"]
    assert info["needs"] == "api_key"


def test_lightningAdapter():
    a = getAdapter("lightning", ModelCfg(apiKey="k", host="https://x.litng.ai"))
    assert a.name == "lightning"
    assert a.isAvail()
    assert not getAdapter("lightning", ModelCfg(apiKey="k")).isAvail()
    assert not getAdapter("lightning", ModelCfg(host="h")).isAvail()
    info = adapterInfo("lightning")
    assert "Lightning" in info["displayName"]
