from labeldesk.core.models.categories import ImgCat
from labeldesk.pipeline.batcher import BatchItem, buildBatches, budgetFor


def test_groupByCat():
    items = [
        BatchItem("a", ImgCat.face),
        BatchItem("b", ImgCat.face),
        BatchItem("c", ImgCat.outdoor),
    ]
    batches = buildBatches(items, batchSz=5)
    cats = {b.cat for b in batches}
    assert ImgCat.face in cats
    assert ImgCat.outdoor in cats


def test_chunking():
    items = [BatchItem(f"x{i}", ImgCat.generic) for i in range(12)]
    batches = buildBatches(items, batchSz=5, adaptive=False)
    assert len(batches) == 3


def test_budgetFor():
    b = budgetFor(ImgCat.face)
    assert b["title"] == 40
