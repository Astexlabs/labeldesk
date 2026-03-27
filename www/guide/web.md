# Web Dashboard

One command brings up the full stack:

```bash
labeldesk web
```

This starts:
- **FastAPI backend** on `:7432`
- **Next.js frontend** on `:3000` (proxies `/api/*` to the backend)

Open http://localhost:3000. `Ctrl-C` stops both.

## First-time setup

The frontend needs its node modules once:

```bash
cd web && npm install
```

## Flags

| flag | does |
|---|---|
| `--api-port N` | change FastAPI port |
| `--ui-port N` | change Next.js port |
| `--host ADDR` | bind address (default `127.0.0.1`) |
| `--api-only` | backend only — skip Next.js (Docker/headless) |

## Pages

- `/` — job list with live status
- `/upload` — drag-drop images + choose options
- `/jobs/[id]` — live progress, results, download CSV/JSON
- `/settings` — provider keys, defaults

## HTTP API

See the [API reference](/reference/api) for all endpoints.
