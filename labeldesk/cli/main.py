import os
import threading
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

from labeldesk.core.config import loadCfg
from labeldesk.core.models.base import ModelCfg
from labeldesk.core.models.registry import getAdapter, listAdapters
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


def _startWeb(host: str, port: int):
    import uvicorn
    from labeldesk.web.app import createApp
    srv = createApp()
    cfg = uvicorn.Config(srv, host=host, port=port, log_level="warning")
    uvicorn.Server(cfg).run()


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
    no_web: bool = typer.Option(
        False, "--no-web",
        help="skip launching the web dashboard alongside",
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

    if not no_web:
        host = cfg.get("default", "web_host", "127.0.0.1")
        port = int(cfg.get("default", "web_port", 7432))
        t = threading.Thread(target=_startWeb, args=(host, port), daemon=True)
        t.start()
        con.print(f"[dim]web dashboard: http://{host}:{port}[/dim]")

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
def serve(
    host: str = typer.Option(None, "--host", help="bind addr (default 127.0.0.1)"),
    port: int = typer.Option(None, "--port", help="bind port (default 7432)"),
):
    """start the web dashboard (fastapi, foreground)."""
    cfg = loadCfg()
    h = host or cfg.get("default", "web_host", "127.0.0.1")
    p = port or int(cfg.get("default", "web_port", 7432))
    con.print(f"[green]serving on http://{h}:{p}[/green]")
    _startWeb(h, p)


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


@modelsApp.command("list")
def modelsList():
    """show every ai backend + whether it's reachable/keyed."""
    cfg = loadCfg()
    tbl = Table(title="models")
    tbl.add_column("name")
    tbl.add_column("available")
    for name in listAdapters():
        try:
            a = _mkAdapter(name, cfg)
            avail = "[green]yes[/green]" if a.isAvail() else "[red]no[/red]"
        except Exception:
            avail = "[red]err[/red]"
        tbl.add_row(name, avail)
    con.print(tbl)


@modelsApp.command("test")
def modelsTest(name: str = typer.Argument(..., help="adapter name, e.g. ollama")):
    """ping one backend to check its key/connection."""
    cfg = loadCfg()
    try:
        a = _mkAdapter(name, cfg)
        if a.isAvail():
            con.print(f"[green]{name} ok[/green]")
        else:
            con.print(f"[yellow]{name} not reachable / no key[/yellow]")
    except Exception as e:
        con.print(f"[red]{name} err: {e}[/red]")


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
    web: bool = typer.Option(False, "--web", help="start web dashboard instead of tui"),
    host: Optional[str] = typer.Option(None, "--host", help="web bind addr"),
    port: Optional[int] = typer.Option(None, "--port", help="web bind port"),
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
    cfg = loadCfg(cfg_file)
    if web:
        h = host or cfg.get("default", "web_host", "127.0.0.1")
        p = port or int(cfg.get("default", "web_port", 7432))
        con.print(f"[green]web dashboard: http://{h}:{p}[/green]")
        _startWeb(h, p)
    else:
        from labeldesk.tui.app import LabelDeskTui
        LabelDeskTui().run()


def main():
    app()


if __name__ == "__main__":
    main()
