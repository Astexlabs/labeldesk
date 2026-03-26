import tempfile
from pathlib import Path

from labeldesk.core.config import loadCfg, Cfg


def test_defaults():
    cfg = loadCfg(Path("/nonexistent"))
    assert cfg.get("default", "model") == "anthropic"
    assert cfg.get("default", "web_port") == 7432


def test_setGet():
    cfg = Cfg(data={})
    cfg.set("foo", "bar", "baz")
    assert cfg.get("foo", "bar") == "baz"


def test_saveLoad():
    with tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False) as f:
        p = Path(f.name)
    cfg = loadCfg(Path("/nonexistent"))
    cfg.set("default", "model", "ollama")
    cfg.save(p)
    reloaded = loadCfg(p)
    assert reloaded.get("default", "model") == "ollama"


def test_envOverride(monkeypatch):
    monkeypatch.setenv("LABELDESK_ANTHROPIC_API_KEY", "sk-test")
    cfg = Cfg(data={"anthropic": {"api_key": "old"}})
    assert cfg.get("anthropic", "api_key") == "sk-test"
