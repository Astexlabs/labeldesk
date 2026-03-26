import os
from pathlib import Path

_IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}


def appDir() -> Path:
    base = os.environ.get("LABELDESK_HOME")
    if base:
        d = Path(base)
    else:
        d = Path.home() / ".labeldesk"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cacheDir() -> Path:
    d = appDir() / ".cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cfgPath() -> Path:
    return appDir() / "config.toml"


def cacheDbPath() -> Path:
    return cacheDir() / "labeldesk_cache.db"


def jobDbPath() -> Path:
    return cacheDir() / "jobs.db"


def uploadDir() -> Path:
    d = cacheDir() / "uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def expandImgPaths(inputs: list[str | Path], recursive: bool = False) -> list[Path]:
    """turn mix of files n dirs into flat list of img paths"""
    out: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if not p.exists():
            continue
        if p.is_file():
            if p.suffix.lower() in _IMG_EXTS:
                out.append(p)
        elif p.is_dir():
            glob = "**/*" if recursive else "*"
            for f in sorted(p.glob(glob)):
                if f.is_file() and f.suffix.lower() in _IMG_EXTS:
                    out.append(f)
    return out
