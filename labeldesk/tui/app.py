from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button, Checkbox, DataTable, Footer, Header, Input, Label,
    Log, Select, Static, TabbedContent, TabPane,
)

from labeldesk.core.config import loadCfg
from labeldesk.core.models.registry import listAdapters
from labeldesk.core.storage.job_store import JobStore


MODES = ["title", "description", "both", "tags"]
OUTPUTS = ["preview", "rename", "copy-rename", "csv", "json", "txt"]


class LabelDeskTui(App):
    """interactive label runner + settings tui"""

    CSS = """
    Screen { align: center middle; }
    #main { width: 90%; height: 90%; border: solid $accent; }
    .row { height: 3; margin: 1 0; }
    .lbl { width: 20; content-align: right middle; padding-right: 2; }
    Input { width: 50; }
    Select { width: 50; }
    Button { margin: 0 1; }
    DataTable { height: 1fr; }
    #run-log { height: 1fr; border: solid $primary; margin-top: 1; }
    #status { dock: bottom; height: 1; background: $boost; }
    """

    BINDINGS = [
        ("q", "quit", "quit"),
        ("s", "save", "save"),
        ("r", "refresh", "refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.cfg = loadCfg()
        self._jobBusy = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main"):
            with TabbedContent(initial="tab-run"):
                with TabPane("run", id="tab-run"):
                    yield from self._runPane()
                with TabPane("settings", id="tab-settings"):
                    yield from self._settingsPane()
                with TabPane("api keys", id="tab-keys"):
                    yield from self._keysPane()
                with TabPane("ollama", id="tab-ollama"):
                    yield from self._ollamaPane()
                with TabPane("history", id="tab-history"):
                    yield DataTable(id="history-tbl")
                with TabPane("cache", id="tab-cache"):
                    yield from self._cachePane()
        yield Static("ready", id="status")
        yield Footer()

    def _runPane(self):
        with Vertical():
            with Horizontal(classes="row"):
                yield Label("img folder:", classes="lbl")
                yield Input(str(Path.cwd()), id="run-path",
                            placeholder="path to imgs or dir")
            with Horizontal(classes="row"):
                yield Label("context:", classes="lbl")
                yield Input("", id="run-ctx",
                            placeholder="e.g. 'vacation pics from italy'")
            with Horizontal(classes="row"):
                yield Label("model:", classes="lbl")
                yield Select([(a, a) for a in listAdapters()],
                             value=self.cfg.get("default", "model"),
                             id="run-model")
            with Horizontal(classes="row"):
                yield Label("mode:", classes="lbl")
                yield Select([(m, m) for m in MODES],
                             value=self.cfg.get("default", "mode", "title"),
                             id="run-mode")
            with Horizontal(classes="row"):
                yield Label("output:", classes="lbl")
                yield Select([(o, o) for o in OUTPUTS],
                             value=self.cfg.get("default", "output", "preview"),
                             id="run-output")
            with Horizontal(classes="row"):
                yield Label("", classes="lbl")
                yield Checkbox("recursive (scan subdirs)", id="run-recursive")
            with Horizontal(classes="row"):
                yield Button("scan", id="run-scan")
                yield Button("run labeling", variant="success", id="run-go")
            yield Log(id="run-log", highlight=True)

    def _settingsPane(self):
        with VerticalScroll():
            with Horizontal(classes="row"):
                yield Label("default model:", classes="lbl")
                yield Select(
                    [(a, a) for a in listAdapters()],
                    value=self.cfg.get("default", "model"),
                    id="default-model",
                )
            with Horizontal(classes="row"):
                yield Label("default mode:", classes="lbl")
                yield Select(
                    [("title", "title"), ("description", "description"),
                     ("both", "both"), ("tags", "tags")],
                    value=self.cfg.get("default", "mode", "title"),
                    id="default-mode",
                )
            with Horizontal(classes="row"):
                yield Label("output fmt:", classes="lbl")
                yield Select(
                    [("preview", "preview"), ("rename", "rename"),
                     ("copy-rename", "copy-rename"), ("csv", "csv"),
                     ("json", "json"), ("txt", "txt")],
                    value=self.cfg.get("default", "output", "preview"),
                    id="default-output",
                )
            with Horizontal(classes="row"):
                yield Label("batch size:", classes="lbl")
                yield Input(str(self.cfg.get("default", "batch_size", 5)), id="batch-size")
            with Horizontal(classes="row"):
                yield Label("web port:", classes="lbl")
                yield Input(str(self.cfg.get("default", "web_port", 7432)), id="web-port")
            yield Button("save settings", variant="primary", id="save-settings")

    def _keysPane(self):
        with VerticalScroll():
            for name in ["anthropic", "openai", "gemini"]:
                with Horizontal(classes="row"):
                    yield Label(f"{name} key:", classes="lbl")
                    yield Input(
                        self.cfg.get(name, "api_key", ""),
                        password=True, id=f"key-{name}",
                    )
                with Horizontal(classes="row"):
                    yield Label(f"{name} model:", classes="lbl")
                    yield Input(
                        self.cfg.get(name, "model_id", ""),
                        id=f"mid-{name}",
                    )
            yield Button("save keys", variant="primary", id="save-keys")

    def _ollamaPane(self):
        with VerticalScroll():
            with Horizontal(classes="row"):
                yield Label("ollama host:", classes="lbl")
                yield Input(
                    self.cfg.get("ollama", "host", "http://localhost:11434"),
                    id="ollama-host",
                )
            with Horizontal(classes="row"):
                yield Label("ollama model:", classes="lbl")
                yield Input(self.cfg.get("ollama", "model_id", "llava"), id="ollama-model")
            with Horizontal(classes="row"):
                yield Button("test connection", id="test-ollama")
                yield Button("save", variant="primary", id="save-ollama")
            yield Static("", id="ollama-status")

    def _cachePane(self):
        with VerticalScroll():
            from labeldesk.core.paths import cacheDir
            yield Static(f"cache dir: {cacheDir()}")
            with Horizontal(classes="row"):
                yield Button("clear result cache", variant="warning", id="clear-cache")
                yield Button("clear job history", variant="warning", id="clear-jobs")
            yield Static("", id="cache-status")

    def on_mount(self):
        self._loadHistory()

    def _loadHistory(self):
        tbl = self.query_one("#history-tbl", DataTable)
        tbl.clear(columns=True)
        tbl.add_columns("id", "status", "files", "model", "mode", "cost")
        store = JobStore()
        for j in store.list(50):
            tbl.add_row(j.id, j.status, f"{j.doneFiles}/{j.totalFiles}",
                        j.adapter, j.mode, f"${j.costUsd:.4f}")
        store.close()

    def _say(self, msg: str):
        self.query_one("#status", Static).update(msg)

    def _log(self, msg: str):
        self.query_one("#run-log", Log).write_line(msg)

    def _grabRunOpts(self) -> dict:
        return {
            "path": self.query_one("#run-path", Input).value.strip(),
            "ctx": self.query_one("#run-ctx", Input).value.strip(),
            "model": self.query_one("#run-model", Select).value,
            "mode": self.query_one("#run-mode", Select).value,
            "output": self.query_one("#run-output", Select).value,
            "recursive": self.query_one("#run-recursive", Checkbox).value,
        }

    def _scanImgs(self, opts: dict | None = None):
        from labeldesk.core.paths import expandImgPaths
        opts = opts or self._grabRunOpts()
        if not opts["path"]:
            self._log("! no path given")
            return []
        imgs = expandImgPaths([opts["path"]], recursive=opts["recursive"])
        self._log(f"found {len(imgs)} imgs in {opts['path']}")
        if not imgs:
            self._log("  (nothing to do - check path or try recursive)")
        return imgs

    @work(thread=True, exclusive=True)
    def _runJob(self, opts: dict, imgs: list):
        from labeldesk.core.models.base import ModelCfg
        from labeldesk.core.models.registry import getAdapter
        from labeldesk.core.output.formatters import fmtResults
        from labeldesk.pipeline.runner import PipelineRunner

        mName = opts["model"]
        sec = self.cfg.section(mName)
        try:
            adapter = getAdapter(mName, ModelCfg(
                apiKey=self.cfg.get(mName, "api_key", ""),
                modelId=sec.get("model_id", ""),
                maxToks=sec.get("max_tokens", 300),
                host=sec.get("host", ""),
            ))
            self.call_from_thread(self._log, f"using {mName}")
        except Exception as e:
            self.call_from_thread(self._log, f"! no adapter ({e}) - heuristic only")
            adapter = None

        store = JobStore()
        job = store.create(
            inputPaths=[str(p) for p in imgs], adapter=mName,
            mode=opts["mode"], outputFmt=opts["output"], totalFiles=len(imgs),
        )
        self.call_from_thread(self._log, f"job {job.id} started")

        def tick(msg, done, total):
            job.doneFiles = done
            store.update(job)
            self.call_from_thread(self._say, f"{msg} {done}/{total}")

        runner = PipelineRunner(
            adapter=adapter, modelName=mName, mode=opts["mode"],
            batchSz=int(self.cfg.get("default", "batch_size", 5)),
            collectionCtx=opts["ctx"], progressCb=tick,
        )
        try:
            results = runner.processMany([opts["path"]], recursive=opts["recursive"])
        finally:
            runner.close()

        job.status = "done"
        job.results = {k: v.asDict() for k, v in results.items()}
        store.update(job)
        store.close()

        out = fmtResults(results, opts["output"])
        self.call_from_thread(self._log, "--- results ---")
        for line in out.splitlines():
            self.call_from_thread(self._log, line)
        self.call_from_thread(self._log, f"done ({len(results)} imgs)")
        self.call_from_thread(self._say, "done")
        self.call_from_thread(self._loadHistory)

    def on_worker_state_changed(self, ev):
        if ev.worker.is_finished:
            self._jobBusy = False

    def on_button_pressed(self, ev: Button.Pressed):
        bid = ev.button.id
        if bid == "run-scan":
            self.query_one("#run-log", Log).clear()
            self._scanImgs()
        elif bid == "run-go":
            if self._jobBusy:
                self._say("already running")
                return
            self.query_one("#run-log", Log).clear()
            opts = self._grabRunOpts()
            imgs = self._scanImgs(opts)
            if not imgs:
                return
            self._jobBusy = True
            self._say("running...")
            self._runJob(opts, imgs)
        elif bid == "save-settings":
            self.cfg.set("default", "model", self.query_one("#default-model", Select).value)
            self.cfg.set("default", "mode", self.query_one("#default-mode", Select).value)
            self.cfg.set("default", "output", self.query_one("#default-output", Select).value)
            self.cfg.set("default", "batch_size", int(self.query_one("#batch-size", Input).value))
            self.cfg.set("default", "web_port", int(self.query_one("#web-port", Input).value))
            self.cfg.save()
            self._say("settings saved")
        elif bid == "save-keys":
            for name in ["anthropic", "openai", "gemini"]:
                self.cfg.set(name, "api_key", self.query_one(f"#key-{name}", Input).value)
                self.cfg.set(name, "model_id", self.query_one(f"#mid-{name}", Input).value)
            self.cfg.save()
            self._say("keys saved")
        elif bid == "save-ollama":
            self.cfg.set("ollama", "host", self.query_one("#ollama-host", Input).value)
            self.cfg.set("ollama", "model_id", self.query_one("#ollama-model", Input).value)
            self.cfg.save()
            self._say("ollama saved")
        elif bid == "test-ollama":
            from labeldesk.core.models.base import ModelCfg
            from labeldesk.core.models.registry import getAdapter
            host = self.query_one("#ollama-host", Input).value
            a = getAdapter("ollama", ModelCfg(host=host))
            ok = a.isAvail()
            self.query_one("#ollama-status", Static).update(
                "[green]connected[/green]" if ok else "[red]unreachable[/red]"
            )
        elif bid == "clear-cache":
            from labeldesk.pipeline.cache import ResultCache
            c = ResultCache()
            c.clear()
            c.close()
            self.query_one("#cache-status", Static).update("result cache cleared")
        elif bid == "clear-jobs":
            store = JobStore()
            for j in store.list(999):
                store.delete(j.id)
            store.close()
            self._loadHistory()
            self.query_one("#cache-status", Static).update("job history cleared")

    def action_save(self):
        self.cfg.save()
        self._say("config saved")

    def action_refresh(self):
        self._loadHistory()
        self._say("refreshed")
