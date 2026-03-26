import os
import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path

from labeldesk.core.paths import cfgPath


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
        p = path or cfgPath()
        lines = []
        for sec, vals in self.data.items():
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


def loadCfg(path: Path | None = None) -> Cfg:
    p = path or cfgPath()
    merged = {k: dict(v) for k, v in _DEFAULTS.items()}
    if p.exists():
        with open(p, "rb") as f:
            user = tomllib.load(f)
        for sec, vals in user.items():
            merged.setdefault(sec, {}).update(vals)
    return Cfg(data=merged)
