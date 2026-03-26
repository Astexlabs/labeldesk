from dataclasses import dataclass, field


@dataclass
class LabelResult:
    title: str = ""
    desc: str = ""
    tags: list[str] = field(default_factory=list)
    src: str = "unknown"
    cached: bool = False
    tokensUsed: int = 0
    costUsd: float = 0.0

    def merge(self, other: "LabelResult") -> "LabelResult":
        return LabelResult(
            title=self.title or other.title,
            desc=self.desc or other.desc,
            tags=self.tags or other.tags,
            src=f"{self.src}+{other.src}",
            cached=self.cached or other.cached,
            tokensUsed=self.tokensUsed + other.tokensUsed,
            costUsd=self.costUsd + other.costUsd,
        )

    def asDict(self) -> dict:
        return {
            "title": self.title,
            "desc": self.desc,
            "tags": self.tags,
            "src": self.src,
            "cached": self.cached,
            "tokensUsed": self.tokensUsed,
            "costUsd": self.costUsd,
        }
