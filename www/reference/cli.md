# CLI Reference

## Root

```bash
labeldesk [OPTIONS] COMMAND
```

| option | description |
|---|---|
| `-c, --config PATH` | explicit YAML/TOML config file (otherwise auto-discovered) |

With no subcommand, opens the interactive TUI.

---

## `labeldesk label`

Run the labeling pipeline on one or more paths.

```bash
labeldesk label PATHS... [OPTIONS]
```

| option | default | description |
|---|---|---|
| `-m, --model NAME` | from config | provider: `anthropic` · `openai` · `gemini` · `groq` · `lightning` · `ollama` |
| `--mode MODE` | `title` | legacy mode: `title` · `description` · `both` · `tags` |
| `-f, --fields SPEC` | — | schema fields: preset name or comma-list (see [schema](/guide/schema)) |
| `-o, --output FMT` | `preview` | `preview` · `rename` · `copy-rename` · `csv` · `json` · `txt` |
| `--out-dir PATH` | — | target dir for `copy-rename`/`csv`/`json`/`txt` |
| `-r, --recursive` | off | scan subdirectories |
| `--batch-size N` | `5` | images per AI batch |
| `--ctx STR` | — | collection hint (e.g. `"wedding photos"`) |
| `--dry-run` | off | estimate cost, don't run |

**Examples**

```bash
labeldesk label ./photos
labeldesk label ./photos -r --fields dataset --output json --out-dir ./out
labeldesk label a.jpg b.png --ctx "product shots" --dry-run
```

---

## `labeldesk schema`

Print every available label field, its type, and the presets. Use the field names with `--fields`.

---

## `labeldesk web`

Launch the web dashboard (FastAPI + Next.js).

| option | default | description |
|---|---|---|
| `--host ADDR` | `127.0.0.1` | API bind address |
| `--api-port N` | `7432` | FastAPI port |
| `--ui-port N` | `3000` | Next.js port |
| `--api-only` | off | skip the Next.js frontend |

---

## `labeldesk tui`

Open the interactive terminal UI. Same as running `labeldesk` with no arguments.

---

## `labeldesk config`

| command | description |
|---|---|
| `config show` | print the whole merged config |
| `config get SECTION.KEY` | read one value (keys masked) |
| `config set SECTION.KEY VALUE` | write one value |

```bash
labeldesk config set default.model groq
labeldesk config set groq.api_key gsk_...
labeldesk config set default.fields dataset
```

---

## `labeldesk models`

| command | description |
|---|---|
| `models list` | show every provider with model ID and readiness |
| `models test NAME` | ping one provider's key/connection |
| `models pick` | interactive picker: choose default + set key |

---

## `labeldesk job`

| command | description |
|---|---|
| `job history [-n LIMIT]` | list recent runs |
| `job show JOB_ID` | full details + results for one run |
