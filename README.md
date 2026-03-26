# labeldesk

smart img labeling pipeline w cascading cost optimization. ai is the **last resort**, not the first call.

## install

```bash
uv sync
uv sync --extra ai      # anthropic/openai/gemini sdks
uv sync --extra onnx    # local classifier
```

## usage

### as a package

```bash
labeldesk                          # opens tui + web dashboard
labeldesk label ./photos           # label imgs in a dir
labeldesk label ./photos -r        # recursive
labeldesk label ./a.jpg ./b.png    # individual files
labeldesk serve                    # web dashboard only
labeldesk tui                      # settings tui only
```

### cli commands

```bash
labeldesk label ./imgs --model ollama --mode title --output csv --out-dir ./out
labeldesk config set anthropic.api_key sk-ant-...
labeldesk config set default.model ollama
labeldesk config show
labeldesk models list
labeldesk models test ollama
labeldesk job history
```

### output modes

| flag | what it does |
|---|---|
| `--output preview` | stdout only, no writes (default) |
| `--output rename` | rename files in place |
| `--output copy-rename` | copy to `--out-dir` with new names |
| `--output csv` / `json` / `txt` | write results file |

## architecture

### the cascading decision tree

```
img -> extract free signals (exif, color, aspect, edges)
    -> heuristic label? (solid color, icon) -> DONE, zero cost
    -> compute phash -> cache hit? -> DONE, zero cost
    -> classify locally (onnx or signal-based)
    -> screenshot/doc? -> ocr + txt-llm (10x cheaper than vision)
    -> else -> homogeneous batch by category -> vision call w per-cat token budget
```

### components

```
labeldesk/
  core/
    config.py          toml config w env overrides
    paths.py           ~/.labeldesk + .cache dir mgmt, dir->files expansion
    models/
      base.py          adapter protocol (vision + txt paths)
      registry.py      @register decorator, auto-discovery
      *_adapter.py     anthropic, openai, gemini, ollama
    output/
      formatters.py    rename/csv/json/txt/preview + fname sanitization
    storage/
      job_store.py     sqlite job history
  pipeline/
    signals.py         free signal extraction (exif, pixel heuristics)
    hasher.py          perceptual hashing + dedup
    classifier.py      onnx mobilenet or signal fallback
    normalizer.py      resize to 768px, jpeg compress for cheap tokens
    batcher.py         homogeneous batching + per-category token budgets
    cache.py           phash-keyed sqlite result cache
    ocr.py             tesseract wrapper
    runner.py          the orchestrator
  cli/main.py          typer cli
  tui/app.py           textual settings ui
  web/app.py           fastapi backend
web/                   nextjs dashboard (proxies to :7432)
```

## web dashboard

backend (fastapi, port 7432):

```
GET  /api/health
GET  /api/models          list adapters + availability
GET  /api/config          safe config (keys masked)
POST /api/config          set key
POST /api/upload          multipart img upload
POST /api/jobs            create labeling job (runs in bg)
GET  /api/jobs            list jobs
GET  /api/jobs/{id}       job status + results
DELETE /api/jobs/{id}
```

frontend (nextjs, port 3000):

```bash
cd web && npm install && npm run dev
```

pages: `/` (job list), `/upload` (drag-drop + opts), `/jobs/[id]` (live progress + download), `/settings`

## tui

`labeldesk tui` — textual terminal ui with tabs:

- **settings** — default model, mode, output fmt, batch size, web port
- **api keys** — anthropic/openai/gemini keys + model ids
- **ollama** — host config + connection test
- **history** — job table
- **cache** — clear result cache / job history

keys: `q` quit, `s` save, `r` refresh

## data locations

everything goes in `~/.labeldesk/` (override via `LABELDESK_HOME`):

```
~/.labeldesk/
  config.toml
  .cache/
    labeldesk_cache.db     phash result cache
    jobs.db                job history
    uploads/               web-uploaded imgs
```

## cost optimization summary

| technique | savings |
|---|---|
| heuristic skip (solid/icon) | 100% for that class |
| phash dedup + cache | 15-40% fewer calls on real libs |
| ocr + txt-llm for screenshots/docs | 80-90% cheaper per img |
| per-category token budgets | 40-60% output token cut |
| homogeneous batching | 20-35% input token cut |
| resize to 768px + jpeg | vision token cost ∝ img size |
| cache on re-runs | near-zero repeat cost |

multiplicative — real-world mixed libs run 5-15x cheaper than naive per-img vision calls.

---

## mcp integration plan

labeldesk exposes enough primitives to be a useful mcp server. here's the plan:

### mcp server (`labeldesk/mcp/server.py`)

use the official `mcp` python sdk, expose via stdio transport so it plugs into claude desktop / any mcp client.

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

srv = Server("labeldesk")
```

### tools to expose

| tool | args | returns |
|---|---|---|
| `label_images` | `paths: list[str]`, `mode`, `model`, `recursive` | dict of `{path: {title, desc, tags, src}}` |
| `label_dir` | `dir: str`, `mode`, `recursive` | same, convenience wrapper |
| `rename_images` | `paths`, `out_dir`, `dry_run` | list of `{from, to}` mappings |
| `describe_image` | `path: str` | single result w full desc |
| `get_image_signals` | `path: str` | raw free signals (exif, color, aspect) — useful for agents to reason about imgs w/o ai |
| `list_models` | — | available adapters + status |
| `estimate_cost` | `paths`, `mode`, `model` | usd estimate before running |

### resources to expose

| uri | what |
|---|---|
| `labeldesk://jobs` | job history json |
| `labeldesk://jobs/{id}` | single job result |
| `labeldesk://config` | current config (keys masked) |
| `labeldesk://cache/stats` | cache hit rate, size |

### why this is useful as mcp

1. **agent img workflows** — an agent managing a file system can call `label_images` on screenshots it took, then reason about them by title rather than re-reading pixels
2. **cost-aware delegation** — the agent calls `estimate_cost` first, decides whether the batch is worth running
3. **free signals for reasoning** — `get_image_signals` gives the agent exif/color/aspect data to make decisions without any ai call at all
4. **composability** — `rename_images` with `dry_run=true` lets the agent preview the plan, then confirm

### install as mcp

add to claude desktop config:

```json
{
  "mcpServers": {
    "labeldesk": {
      "command": "uvx",
      "args": ["labeldesk", "mcp"]
    }
  }
}
```

### implementation notes

- reuse `PipelineRunner` directly — mcp tools are thin wrappers
- jobs created via mcp still land in the shared `jobs.db` so they show up in tui/web
- stdio transport means no port conflicts with the web server
- progress can stream back via mcp notifications for long batches
- the `adapter=None` fallback (heuristic-only) means mcp works even with zero api keys configured — useful for quick metadata extraction

add `mcp>=1.0` to optional deps, new cli subcommand `labeldesk mcp` that calls `stdio_server(srv)`.
