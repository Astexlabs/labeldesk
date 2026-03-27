from dataclasses import dataclass, field


@dataclass
class LabelResult:
    title: str = ""
    desc: str = ""
    tags: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)
    src: str = "unknown"
    cached: bool = False
    tokensUsed: int = 0
    costUsd: float = 0.0

    def merge(self, other: "LabelResult") -> "LabelResult":
        ex = dict(other.extra)
        ex.update(self.extra)
        return LabelResult(
            title=self.title or other.title,
            desc=self.desc or other.desc,
            tags=self.tags or other.tags,
            extra=ex,
            src=f"{self.src}+{other.src}",
            cached=self.cached or other.cached,
            tokensUsed=self.tokensUsed + other.tokensUsed,
            costUsd=self.costUsd + other.costUsd,
        )

    def get(self, key: str, fallback=None):
        if key == "title":
            return self.title
        if key == "desc":
            return self.desc
        if key == "tags":
            return self.tags
        return self.extra.get(key, fallback)

    def asDict(self) -> dict:
        d = {
            "title": self.title,
            "desc": self.desc,
            "tags": self.tags,
            "src": self.src,
            "cached": self.cached,
            "tokensUsed": self.tokensUsed,
            "costUsd": self.costUsd,
        }
        d.update(self.extra)
        return d

    @classmethod
    def fromFields(cls, data: dict, src: str = "vision") -> "LabelResult":
        core = {"title", "desc", "tags"}
        r = cls(
            title=data.get("title", ""),
            desc=data.get("desc", ""),
            tags=data.get("tags") or [],
            extra={k: v for k, v in data.items() if k not in core},
            src=src,
        )
        if not r.title and "suggested_fname" in r.extra:
            r.title = r.extra["suggested_fname"]
        return r
