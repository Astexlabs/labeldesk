from dataclasses import dataclass, field


@dataclass
class LabelResult:
    title: str = ""
    desc: str = ""
    tags: list[str] = field(default_factory=list)
    src: str = "unknown"
    cached: bool = False

    def merge(self, other: "LabelResult") -> "LabelResult":
        return LabelResult(
            title=self.title or other.title,
            desc=self.desc or other.desc,
            tags=self.tags or other.tags,
            src=f"{self.src}+{other.src}",
            cached=self.cached or other.cached,
        )
