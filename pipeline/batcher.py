from dataclasses import dataclass, field
from pathlib import Path

from core.models.categories import ImgCat

TOKEN_BUDGETS = {
    ImgCat.face: {"title": 40, "desc": 80, "tags": 20},
    ImgCat.product: {"title": 50, "desc": 100, "tags": 30},
    ImgCat.document: {"title": 60, "desc": 0, "tags": 0},
    ImgCat.screenshot: {"title": 50, "desc": 0, "tags": 0},
    ImgCat.outdoor: {"title": 50, "desc": 100, "tags": 40},
    ImgCat.diagram: {"title": 60, "desc": 0, "tags": 0},
    ImgCat.generic: {"title": 60, "desc": 120, "tags": 40},
    ImgCat.indoor: {"title": 50, "desc": 100, "tags": 30},
    ImgCat.food: {"title": 50, "desc": 100, "tags": 30},
    ImgCat.abstract: {"title": 50, "desc": 100, "tags": 30},
    ImgCat.icon: {"title": 40, "desc": 0, "tags": 0},
}


@dataclass
class BatchItem:
    imgPath: str
    cat: ImgCat
    ctx: str = ""


@dataclass
class Batch:
    cat: ImgCat
    items: list[BatchItem] = field(default_factory=list)
    maxToks: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.maxToks:
            self.maxToks = TOKEN_BUDGETS.get(
                self.cat, TOKEN_BUDGETS[ImgCat.generic]
            )


def buildBatches(
    items: list[BatchItem],
    batchSz: int = 5,
    adaptive: bool = True,
) -> list[Batch]:
    """group items by cat, then chunk into batches"""
    buckets: dict[ImgCat, list[BatchItem]] = {}
    for item in items:
        buckets.setdefault(item.cat, []).append(item)

    batches = []
    for cat, catItems in buckets.items():
        sz = batchSz
        if adaptive:
            budget = TOKEN_BUDGETS.get(cat, TOKEN_BUDGETS[ImgCat.generic])
            totalBudget = sum(budget.values())
            if totalBudget < 100:
                sz = min(10, len(catItems))
            elif totalBudget > 200:
                sz = max(3, sz)
        for i in range(0, len(catItems), sz):
            chunk = catItems[i : i + sz]
            batches.append(Batch(cat=cat, items=chunk))
    return batches


def budgetFor(cat: ImgCat) -> dict:
    return TOKEN_BUDGETS.get(cat, TOKEN_BUDGETS[ImgCat.generic])
