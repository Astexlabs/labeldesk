# Configuration Reference

## Lookup order

1. `LABELDESK_<SECTION>_<KEY>` environment variable
2. `./labeldesk.yaml` (or `.yml`) in the current directory
3. `~/.labeldesk/config.yaml`
4. `~/.labeldesk/config.toml`
5. Built-in defaults

Each layer overrides the ones below it.

## Sections

### `[default]`

| key | type | default | description |
|---|---|---|---|
| `model` | str | `anthropic` | default provider name |
| `mode` | str | `title` | legacy single-field mode |
| `fields` | str | — | schema preset or comma-list (overrides `mode` when set) |
| `output` | str | `preview` | default output format |
| `batch_size` | int | `5` | images per AI batch |
| `web_host` | str | `127.0.0.1` | dashboard bind address |
| `web_port` | int | `7432` | FastAPI port |

### Provider sections

Each provider has its own section: `[anthropic]`, `[openai]`, `[gemini]`, `[groq]`, `[lightning]`, `[ollama]`.

| key | applies to | description |
|---|---|---|
| `api_key` | all except ollama | provider API key |
| `model_id` | all | model identifier |
| `max_tokens` | all | per-call token cap |
| `host` | ollama, lightning | endpoint URL |

### `[cost]`

| key | default | description |
|---|---|---|
| `warn_above_usd` | `0.50` | print a warning before jobs over this cost |
| `abort_above_usd` | `5.00` | refuse to run without confirmation |

### `[pipeline]`

| key | default | description |
|---|---|---|
| `max_img_side` | `768` | resize longest edge before vision inference |
| `jpeg_quality` | `75` | recompression quality |
| `cache_ttl_days` | `30` | cache entry expiry |
| `onnx_model` | — | path to local classifier |

## Full example

```yaml
default:
  model: groq
  fields: dataset
  output: json
  batch_size: 8

groq:
  api_key: gsk_...
  model_id: llama-3.2-11b-vision-preview

lightning:
  api_key: lai_...
  host: https://8000-01hxxx.cloudspaces.litng.ai
  model_id: llava-1.6-34b

cost:
  warn_above_usd: 1.00
```
