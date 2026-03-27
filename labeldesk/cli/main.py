import os
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

from labeldesk.core.config import loadCfg
from labeldesk.core.models.base import ModelCfg
from labeldesk.core.models.registry import getAdapter, listAdapters, adapterInfo
from labeldesk.core.output.formatters import fmtResults
from labeldesk.core.paths import expandImgPaths
from labeldesk.core.storage.job_store import JobStore
from labeldesk.pipeline.runner import PipelineRunner

app = typer.Typer(
    help="""labeldesk - smart img labeler w cascading cost optimization.

\b
quick start:
  labeldesk                      open interactive tui (pick folder + run)
  labeldesk label ./pics         label a folder right now
  labeldesk web                  launch web dashboard (api + ui)
  labeldesk config show          see current settings
  labeldesk models list          check which ai backends are ready""",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
cfgApp = typer.Typer(help="get/set config values (model, api keys, defaults)")
modelsApp = typer.Typer(help="list + test ai model backends")
jobApp = typer.Typer(help="browse past labeling runs")
app.add_typer(cfgApp, name="config")
app.add_typer(modelsApp, name="models")
app.add_typer(jobApp, name="job")

con = Console()


def _startApi(host: str, port: int):
    import uvicorn
    from labeldesk.web.app import createApp
    srv = createApp()
    cfg = uvicorn.Config(srv, host=host, port=port, log_level="warning")
    uvicorn.Server(cfg).run()


import importlib.resources

def _findWebDir() -> Path | None:
    try:
        web_path = importlib.resources.files('labeldesk').joinpath('web')
        if web_path.joinpath('package.json').is_file():
            return Path(str(web_path))
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    # Fallback to original logic for development environments
    here = Path(__file__).resolve()
    for p in [*here.parents, Path.cwd()]:
        cand = p / "web" / "package.json"
        if cand.exists():
            return cand.parent
    return None


def _npmCmd(webDir: Path, uiPort: int) -> list[str]:
    npm = shutil.which("npm")
    if not npm:
        return []
    hasBuild = (webDir / ".next").exists()
    script = "start" if hasBuild else "dev"
    return [npm, "run", script, "--", "-p", str(uiPort)]


def _mkAdapter(name: str, cfg):
    sec = cfg.section(name)
    mcfg = ModelCfg(
        apiKey=cfg.get(name, "api_key", ""),
        modelId=sec.get("model_id", ""),
        maxToks=sec.get("max_tokens", 300),
        host=sec.get("host", ""),
    )
    return getAdapter(name, mcfg)


@app.command()
def label(
    paths: list[str] = typer.Argument(..., help="img files or dirs to label"),
    model: Optional[str] = typer.Option(
        None, "--model", "-m",
        help="ai backend: anthropic | openai | gemini | ollama (default from config)",
    ),
    mode: str = typer.Option(
        "title", "--mode",
        help="what to generate: title | description | both | tags",
    ),
    output: str = typer.Option(
        "preview", "--output", "-o",
        help="result fmt: preview | rename | copy-rename | csv | json | txt",
    ),
    out_dir: Optional[Path] = typer.Option(
        None, "--out-dir",
        help="where to write files (for copy-rename/csv/json/txt)",
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r",
        help="scan subdirs too",
    ),
    batch_size: int = typer.Option(
        5, "--batch-size",
        help="imgs per ai batch (bigger = cheaper but slower feedback)",
    ),
    ctx: str = typer.Option(
        "", "--ctx",
        help="collection hint, e.g. 'wedding photos' - improves labels",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="estimate cost + count imgs, don't actually run",
    ),
):
    """run the labeling pipeline on imgs.

    \b
    examples:
      labeldesk label ./photos
      labeldesk label ./photos -r --mode tags --output json
      labeldesk label a.jpg b.png --ctx "product shots" --dry-run
    """
    cfg = loadCfg()
    modelName = model or cfg.get("default", "model", "anthropic")

    imgPaths = expandImgPaths(paths, recursive=recursive)
    if not imgPaths:
        con.print("[red]no imgs found[/red]")
        raise typer.Exit(1)

    con.print(f"[cyan]found {len(imgPaths)} imgs[/cyan]")

    try:
        adapter = _mkAdapter(modelName, cfg)
    except Exception as e:
        con.print(f"[yellow]no adapter ({e}), running heuristic-only[/yellow]")
        adapter = None

    if dry_run:
        if adapter:
            est = adapter.estimateCost(len(imgPaths), mode)
            con.print(f"[yellow]est cost: ${est:.4f}[/yellow]")
        con.print("[dim]dry run - no changes made[/dim]")
        return

    store = JobStore()
    job = store.create(
        inputPaths=[str(p) for p in imgPaths],
        adapter=modelName, mode=mode, outputFmt=output,
        totalFiles=len(imgPaths),
    )

    with Progress(
        SpinnerColumn(), TextColumn("[cyan]{task.description}"),
        BarColumn(), TextColumn("{task.completed}/{task.total}"),
    ) as prog:
        task = prog.add_task("labeling...", total=len(imgPaths))

        def tick(msg, done, total):
            prog.update(task, completed=done, description=msg)
            job.doneFiles = done
            store.update(job)

        runner = PipelineRunner(
            adapter=adapter, modelName=modelName, mode=mode,
            batchSz=batch_size, collectionCtx=ctx, progressCb=tick,
        )
        results = runner.processMany(paths, recursive=recursive)
        runner.close()

    job.status = "done"
    job.results = {k: v.asDict() for k, v in results.items()}
    store.update(job)
    store.close()

    out = fmtResults(results, output, outDir=out_dir)
    con.print(out)


@app.command()
def web(
    host: str = typer.Option(None, "--host", help="api bind addr (default 127.0.0.1)"),
    api_port: int = typer.Option(None, "--api-port", help="fastapi port (default 7432)"),
    ui_port: int = typer.Option(3000, "--ui-port", help="nextjs port"),
    api_only: bool = typer.Option(
        False, "--api-only",
        help="just the fastapi backend, skip nextjs (for docker/headless)",
    ),
):
    """launch the full web dashboard: fastapi backend + nextjs frontend together.

    \b
    open http://localhost:3000 once it's up.
    ctrl-c stops both.
    """
    cfg = loadCfg()
    h = host or cfg.get("default", "web_host", "127.0.0.1")
    ap = api_port or int(cfg.get("default", "web_port", 7432))

    if api_only:
        con.print(f"[green]api on http://{h}:{ap}[/green]")
        _startApi(h, ap)
        return

    webDir = _findWebDir()
    if not webDir:
        con.print("[red]can't find web/ dir - nextjs frontend missing[/red]")
        con.print(f"[dim]falling back to api only on http://{h}:{ap}[/dim]")
        _startApi(h, ap)
        return

    cmd = _npmCmd(webDir, ui_port)
    if not cmd:
        con.print("[red]npm not on PATH - install node to run the frontend[/red]")
        con.print(f"[dim]falling back to api only on http://{h}:{ap}[/dim]")
        _startApi(h, ap)
        return

    apiT = threading.Thread(target=_startApi, args=(h, ap), daemon=True)
    apiT.start()
    con.print(f"[dim]api: http://{h}:{ap}[/dim]")

    con.print(f"[green]dashboard: http://localhost:{ui_port}[/green]")
    con.print(f"[dim]starting nextjs from {webDir}...[/dim]")
    ui = subprocess.Popen(cmd, cwd=webDir)

    def stop(sig, frm):
        con.print("\n[yellow]shutting down...[/yellow]")
        ui.terminate()
        try:
            ui.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ui.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    ui.wait()


@app.command()
def tui():
    """open the interactive terminal ui - pick a folder, set opts, run labeling."""
    from labeldesk.tui.app import LabelDeskTui
    LabelDeskTui().run()


@cfgApp.command("set")
def cfgSet(
    key: str = typer.Argument(..., help="section.key, e.g. anthropic.api_key"),
    value: str = typer.Argument(..., help="the value to store"),
):
    """set a config value.

    \b
    examples:
      labeldesk config set default.model ollama
      labeldesk config set anthropic.api_key sk-ant-...
    """
    cfg = loadCfg()
    if "." not in key:
        con.print("[red]use section.key fmt[/red]")
        raise typer.Exit(1)
    sec, k = key.split(".", 1)
    cfg.set(sec, k, value)
    cfg.save()
    con.print(f"[green]set {sec}.{k}[/green]")


@cfgApp.command("get")
def cfgGet(key: str = typer.Argument(..., help="section.key to read")):
    """read one config value (keys are masked)."""
    cfg = loadCfg()
    sec, k = key.split(".", 1)
    val = cfg.get(sec, k)
    if sec.endswith("key") or "key" in k:
        val = val[:8] + "..." if val else "(not set)"
    con.print(val)


@cfgApp.command("show")
def cfgShow():
    """print the whole merged config as a table."""
    cfg = loadCfg()
    tbl = Table(title="config")
    tbl.add_column("section")
    tbl.add_column("key")
    tbl.add_column("value")
    for sec, vals in cfg.data.items():
        for k, v in vals.items():
            if "key" in k and v:
                v = str(v)[:8] + "..."
            tbl.add_row(sec, k, str(v))
    con.print(tbl)


def _modelRows(cfg):
    dflt = cfg.get("default", "model", "")
    for name in listAdapters():
        info = adapterInfo(name)
        sec = cfg.section(name)
        mid = sec.get("model_id") or info["defaultModelId"]
        try:
            a = _mkAdapter(name, cfg)
            ok = a.isAvail()
            why = "" if ok else ("no key" if info["needs"] == "api_key" else "unreachable")
        except Exception as e:
            ok, why = False, str(e)[:40]
        yield name, info, mid, ok, why, (name == dflt)


@modelsApp.command("list")
def modelsList():
    """show every ai backend w display name, model id, status."""
    cfg = loadCfg()
    tbl = Table(title="models", show_lines=False)
    tbl.add_column("", width=2)
    tbl.add_column("provider", style="bold")
    tbl.add_column("model id", style="dim")
    tbl.add_column("status")
    tbl.add_column("note", style="dim")
    for name, info, mid, ok, why, isDflt in _modelRows(cfg):
        mark = "[cyan]●[/cyan]" if isDflt else " "
        stat = "[green]ready[/green]" if ok else f"[red]✗[/red]"
        tbl.add_row(mark, info["displayName"], mid, stat, why or info["desc"])
    con.print(tbl)
    con.print("[dim]● = default · change with: labeldesk models pick[/dim]")


@modelsApp.command("pick")
def modelsPick():
    """interactively pick default model + set its key if needed."""
    cfg = loadCfg()
    rows = list(_modelRows(cfg))
    con.print("[bold]pick a default model:[/bold]\n")
    for i, (name, info, mid, ok, why, isDflt) in enumerate(rows, 1):
        stat = "[green]ready[/green]" if ok else f"[yellow]{why}[/yellow]"
        mark = "[cyan]●[/cyan] " if isDflt else "  "
        con.print(f"  {mark}[bold]{i}[/bold]. {info['displayName']:<22} "
                  f"[dim]{mid}[/dim]  {stat}")
        con.print(f"       [dim]{info['desc']}[/dim]")
    n = typer.prompt("\nnumber", type=int)
    if not 1 <= n <= len(rows):
        con.print("[red]bad pick[/red]")
        raise typer.Exit(1)
    name, info, mid, ok, why, _ = rows[n - 1]
    cfg.set("default", "model", name)

    if not ok and info["needs"] == "api_key":
        key = typer.prompt(f"{info['displayName']} api key", hide_input=True, default="")
        if key:
            cfg.set(name, "api_key", key)
    elif not ok and info["needs"] == "host":
        host = typer.prompt("ollama host", default="http://localhost:11434")
        cfg.set(name, "host", host)

    newMid = typer.prompt("model id", default=mid)
    if newMid != mid:
        cfg.set(name, "model_id", newMid)

    cfg.save()
    con.print(f"[green]✓ default → {info['displayName']} ({newMid})[/green]")


@modelsApp.command("test")
def modelsTest(name: str = typer.Argument(..., help="adapter name, e.g. ollama")):
    """ping one backend to check its key/connection."""
    cfg = loadCfg()
    info = adapterInfo(name)
    try:
        a = _mkAdapter(name, cfg)
        if a.isAvail():
            con.print(f"[green]✓ {info['displayName']} ready[/green]")
        else:
            hint = f"set key: labeldesk config set {name}.api_key ..." \
                if info["needs"] == "api_key" else f"check {name}.host is running"
            con.print(f"[yellow]✗ {info['displayName']} not ready[/yellow]")
            con.print(f"[dim]  {hint}[/dim]")
    except Exception as e:
        con.print(f"[red]✗ {name}: {e}[/red]")


@jobApp.command("history")
def jobHistory(limit: int = typer.Option(20, "--limit", "-n", help="max rows")):
    """list recent labeling runs (newest first)."""
    store = JobStore()
    tbl = Table(title="jobs")
    for c in ["id", "status", "files", "model", "mode", "cost"]:
        tbl.add_column(c)
    for j in store.list(limit):
        tbl.add_row(j.id, j.status, f"{j.doneFiles}/{j.totalFiles}",
                    j.adapter, j.mode, f"${j.costUsd:.4f}")
    con.print(tbl)
    store.close()


@jobApp.command("show")
def jobShow(job_id: str = typer.Argument(..., help="job id from history")):
    """dump full details + results for one job."""
    store = JobStore()
    j = store.get(job_id)
    if not j:
        con.print("[red]not found[/red]")
        raise typer.Exit(1)
    con.print(j)
    store.close()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    cfg_file: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="explicit yaml/toml config file (else auto-discover)",
    ),
):
    """with no subcmd: opens the interactive tui where u can pick imgs + run."""
    if cfg_file:
        os.environ["LABELDESK_CONFIG"] = str(cfg_file)
    if ctx.invoked_subcommand is not None:
        return
    from labeldesk.tui.app import LabelDeskTui
    LabelDeskTui().run()


def main():
    app()


if __name__ == "__main__":
    main()
