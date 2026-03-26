from core.models.categories import ImgCat
from pipeline.batcher import BatchItem, Batch, buildBatches, budgetFor, TOKEN_BUDGETS


def test_budgetForKnownCat():
    b = budgetFor(ImgCat.face)
    assert b["title"] == 40
    assert b["desc"] == 80
    assert b["tags"] == 20


def test_budgetForGenericFallback():
    b = budgetFor(ImgCat.generic)
    assert b["title"] == 60


def test_buildBatchesGroupsByCat():
    items = [
        BatchItem(imgPath="a.jpg", cat=ImgCat.face),
        BatchItem(imgPath="b.jpg", cat=ImgCat.face),
        BatchItem(imgPath="c.jpg", cat=ImgCat.outdoor),
    ]
    batches = buildBatches(items, batchSz=5)
    cats = [b.cat for b in batches]
    assert ImgCat.face in cats
    assert ImgCat.outdoor in cats


def test_buildBatchesRespectsSz():
    items = [BatchItem(imgPath=f"{i}.jpg", cat=ImgCat.generic) for i in range(12)]
    batches = buildBatches(items, batchSz=5, adaptive=False)
    sizes = [len(b.items) for b in batches]
    assert sizes == [5, 5, 2]


def test_batchPostInit():
    b = Batch(cat=ImgCat.document)
    assert b.maxToks["title"] == 60
    assert b.maxToks["desc"] == 0


def test_allCatsHaveBudgets():
    for cat in ImgCat:
        assert cat in TOKEN_BUDGETS
