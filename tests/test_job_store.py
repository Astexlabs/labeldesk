import tempfile

from labeldesk.core.storage.job_store import JobStore


def test_createGet():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = JobStore(dbPath=f.name)
        j = s.create(adapter="test", mode="title", totalFiles=5)
        got = s.get(j.id)
        assert got.adapter == "test"
        assert got.totalFiles == 5
        s.close()


def test_update():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = JobStore(dbPath=f.name)
        j = s.create()
        j.status = "done"
        j.doneFiles = 3
        s.update(j)
        got = s.get(j.id)
        assert got.status == "done"
        assert got.doneFiles == 3
        s.close()


def test_list():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = JobStore(dbPath=f.name)
        s.create()
        s.create()
        assert len(s.list()) == 2
        s.close()


def test_delete():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = JobStore(dbPath=f.name)
        j = s.create()
        s.delete(j.id)
        assert s.get(j.id) is None
        s.close()
