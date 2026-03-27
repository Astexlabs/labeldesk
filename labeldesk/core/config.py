import os
import stat
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from labeldesk.core.paths import cfgPath, credsPath, appDir

_SECRET_KEYS = {"api_key"}


def _isSecret(key: str) -> bool:
    return key in _SECRET_KEYS or key.endswith("_key")


def _writeToml(p: Path, data: dict, mode: int | None = None):
    lines = []
    for sec, vals in data.items():
        if not vals:
            continue
        lines.append(f"[{sec}]")
        for k, v in vals.items():
            if isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, bool):
                lines.append(f"{k} = {'true' if v else 'false'}")
            else:
                lines.append(f"{k} = {v}")
        lines.append("")
    p.write_text("\n".join(lines))
    if mode is not None:
        try:
            os.chmod(p, mode)
        except OSError:
            pass


_DEFAULTS = {
    "default": {
        "model": "anthropic",
        "mode": "title",
        "output": "preview",
        "batch_size": 5,
        "web_port": 7432,
        "web_host": "127.0.0.1",
    },
    "anthropic": {"api_key": "", "model_id": "claude-haiku-4-5-20251001", "max_tokens": 300},
    "openai": {"api_key": "", "model_id": "gpt-4o-mini", "max_tokens": 300},
    "gemini": {"api_key": "", "model_id": "gemini-1.5-flash", "max_tokens": 300},
    "groq": {"api_key": "", "model_id": "llama-3.2-11b-vision-preview", "max_tokens": 300},
    "lightning": {"api_key": "", "host": "", "model_id": "lightning-vision", "max_tokens": 300},
    "ollama": {"host": "http://localhost:11434", "model_id": "llava", "max_tokens": 300},
    "cost": {"warn_above_usd": 0.50, "abort_above_usd": 5.00},
}


@dataclass
class Cfg:
    data: dict = field(default_factory=dict)

    def get(self, section: str, key: str, fallback=None):
        env = os.environ.get(f"LABELDESK_{section.upper()}_{key.upper()}")
        if env:
            return env
        return self.data.get(section, {}).get(key, fallback)

    def set(self, section: str, key: str, val):
        self.data.setdefault(section, {})[key] = val

    def section(self, name: str) -> dict:
        return self.data.get(name, {})

    def save(self, path: Path | None = None):
        """split secrets into creds file (0600), rest into main cfg"""
        pub, sec = {}, {}
        for s, vals in self.data.items():
            for k, v in vals.items():
                tgt = sec if (_isSecret(k) and v) else pub
                tgt.setdefault(s, {})[k] = v
        p = path or cfgPath()
        if any(x in (".yaml", ".yml") for x in p.suffixes):
            p.write_text(yaml.safe_dump(pub, sort_keys=False))
        else:
            _writeToml(p, pub)
        if sec:
            _writeToml(credsPath(), sec, mode=stat.S_IRUSR | stat.S_IWUSR)


def _findCfgFile() -> Path | None:
    """look for cfg in cwd then home, yaml > toml"""
    for base in [Path.cwd(), appDir()]:
        for name in ["labeldesk.yaml", "labeldesk.yml", "config.yaml", "config.toml"]:
            p = base / name
            if p.exists():
                return p
    return None


def _isYaml(p: Path) -> bool:
    return any(s in (".yaml", ".yml") for s in p.suffixes)


def _mergeFile(p: Path, into: dict):
    if not p.exists():
        return
    if _isYaml(p):
        user = yaml.safe_load(p.read_text()) or {}
    else:
        with open(p, "rb") as f:
            user = tomllib.load(f)
    for sec, vals in user.items():
        if isinstance(vals, dict):
            into.setdefault(sec, {}).update(vals)


def loadCfg(path: Path | None = None) -> Cfg:
    p = path or _findCfgFile() or cfgPath()
    merged = {k: dict(v) for k, v in _DEFAULTS.items()}
    _mergeFile(p, merged)
    _mergeFile(credsPath(), merged)
    return Cfg(data=merged)
