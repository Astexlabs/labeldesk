import tempfile
from pathlib import Path

from PIL import Image
from textual.widgets import Button, Checkbox, Input, Log, Select, Static

from labeldesk.tui.app import LabelDeskTui, MODES, OUTPUTS


async def test_runTabIsDefault():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        tabs = app.query_one("TabbedContent")
        assert tabs.active == "tab-run"


async def test_runPaneHasAllInputs():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        assert app.query_one("#run-path", Input)
        assert app.query_one("#run-ctx", Input)
        assert app.query_one("#run-model", Select)
        assert app.query_one("#run-mode", Select)
        assert app.query_one("#run-output", Select)
        assert app.query_one("#run-recursive", Checkbox)
        assert app.query_one("#run-log", Log)


async def test_grabRunOptsReadsWidgets():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        app.query_one("#run-path", Input).value = "/tmp/pics"
        app.query_one("#run-ctx", Input).value = "test ctx"
        app.query_one("#run-recursive", Checkbox).value = True
        opts = app._grabRunOpts()
        assert opts["path"] == "/tmp/pics"
        assert opts["ctx"] == "test ctx"
        assert opts["recursive"] is True
        assert opts["mode"] in MODES
        assert opts["output"] in OUTPUTS


async def test_scanEmptyDirLogsNothing():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        d = tempfile.mkdtemp()
        app.query_one("#run-path", Input).value = d
        imgs = app._scanImgs()
        assert imgs == []
        log = app.query_one("#run-log", Log)
        assert log.line_count > 0


async def test_scanFindsImgs():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        d = tempfile.mkdtemp()
        Image.new("RGB", (32, 32), (255, 0, 0)).save(Path(d) / "a.png")
        Image.new("RGB", (32, 32), (0, 255, 0)).save(Path(d) / "b.jpg")
        app.query_one("#run-path", Input).value = d
        imgs = app._scanImgs()
        assert len(imgs) == 2


async def test_scanNoPathWarns():
    app = LabelDeskTui()
    async with app.run_test() as pilot:
        app.query_one("#run-path", Input).value = ""
        imgs = app._scanImgs()
        assert imgs == []


async def test_runJobEndToEnd():
    app = LabelDeskTui()
    async with app.run_test(size=(120, 50)) as pilot:
        d = tempfile.mkdtemp()
        Image.new("RGB", (48, 48), (255, 0, 0)).save(Path(d) / "solid.png")
        app.query_one("#run-path", Input).value = d
        app.query_one("#run-output", Select).value = "preview"
        app.query_one("#run-go", Button).press()
        await pilot.pause()
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert app._jobBusy is False
        log = app.query_one("#run-log", Log)
        txt = "\n".join(str(ln) for ln in log.lines)
        assert "job" in txt
        assert "done" in txt


async def test_runBlocksWhileBusy():
    app = LabelDeskTui()
    async with app.run_test(size=(120, 50)) as pilot:
        app._jobBusy = True
        app.query_one("#run-go", Button).press()
        await pilot.pause()
        status = app.query_one("#status", Static)
        assert "already running" in str(status.render())
