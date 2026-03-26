import csv
import json
import re
import shutil
from io import StringIO
from pathlib import Path

from labeldesk.core.models.result import LabelResult


def sanitizeFname(title: str, maxLen: int = 80) -> str:
    s = re.sub(r"[^\w\s-]", "", title.lower())
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:maxLen].strip("-") or "untitled"


def _resolveCollision(p: Path) -> Path:
    if not p.exists():
        return p
    stem, suf = p.stem, p.suffix
    i = 2
    while True:
        cand = p.parent / f"{stem}-{i}{suf}"
        if not cand.exists():
            return cand
        i += 1


def fmtResults(results: dict[str, LabelResult], fmt: str, outDir: Path | None = None) -> str:
    """write results in chosen fmt, return summary or output path"""
    if fmt == "preview":
        lines = []
        for p, r in results.items():
            lines.append(f"{Path(p).name}: {r.title} [{r.src}]")
        return "\n".join(lines)

    if fmt == "json":
        data = {p: r.asDict() for p, r in results.items()}
        out = json.dumps(data, indent=2)
        if outDir:
            f = outDir / "labels.json"
            f.write_text(out)
            return str(f)
        return out

    if fmt == "csv":
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["original", "title", "desc", "tags", "src"])
        for p, r in results.items():
            w.writerow([p, r.title, r.desc, "|".join(r.tags), r.src])
        out = buf.getvalue()
        if outDir:
            f = outDir / "labels.csv"
            f.write_text(out)
            return str(f)
        return out

    if fmt == "txt":
        lines = []
        for p, r in results.items():
            lines.append(f"== {Path(p).name} ==")
            lines.append(f"title: {r.title}")
            if r.desc:
                lines.append(f"desc: {r.desc}")
            if r.tags:
                lines.append(f"tags: {', '.join(r.tags)}")
            lines.append("")
        out = "\n".join(lines)
        if outDir:
            f = outDir / "labels.txt"
            f.write_text(out)
            return str(f)
        return out

    if fmt in ("rename", "copy-rename"):
        target = outDir or Path(".")
        target.mkdir(parents=True, exist_ok=True)
        moved = []
        for p, r in results.items():
            src = Path(p)
            if not src.exists() or not r.title or r.src in ("error", "none"):
                continue
            newName = sanitizeFname(r.title) + src.suffix.lower()
            dst = _resolveCollision(target / newName)
            if fmt == "rename":
                src.rename(dst)
            else:
                shutil.copy2(src, dst)
            moved.append(f"{src.name} -> {dst.name}")
        return "\n".join(moved)

    return f"unknown fmt: {fmt}"
