from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button, DataTable, Footer, Header, Input, Label,
    Select, Static, TabbedContent, TabPane,
)

from labeldesk.core.config import loadCfg
from labeldesk.core.models.registry import listAdapters
from labeldesk.core.storage.job_store import JobStore


class LabelDeskTui(App):
    """interactive settings + history tui"""

    CSS = """
    Screen { align: center middle; }
    #main { width: 90%; height: 90%; border: solid $accent; }
    .row { height: 3; margin: 1 0; }
    .lbl { width: 20; content-align: right middle; padding-right: 2; }
    Input { width: 50; }
    Select { width: 50; }
    Button { margin: 0 1; }
    DataTable { height: 1fr; }
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main"):
            with TabbedContent():
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

    def on_button_pressed(self, ev: Button.Pressed):
        bid = ev.button.id
        if bid == "save-settings":
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
