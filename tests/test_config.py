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


def test_yamlLoad():
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write("default:\n  model: gemini\n  batch_size: 8\n")
        p = Path(f.name)
    cfg = loadCfg(p)
    assert cfg.get("default", "model") == "gemini"
    assert cfg.get("default", "batch_size") == 8
    assert cfg.get("default", "web_port") == 7432


def test_yamlSave():
    import tempfile
    from pathlib import Path
    p = Path(tempfile.mktemp(suffix=".yaml"))
    cfg = loadCfg(Path("/nonexistent"))
    cfg.set("ollama", "host", "http://test:11434")
    cfg.save(p)
    txt = p.read_text()
    assert "ollama:" in txt
    assert "http://test:11434" in txt
