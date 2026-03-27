# Architecture

## The cascading decision tree

```
image
  ↓
extract free signals (EXIF, dominant color, aspect, edge density)
  ↓
heuristic label?       ───────────► DONE (zero cost)
  (solid color, icon)
  ↓
perceptual hash → cache hit? ─────► DONE (zero cost)
  ↓
classify locally (ONNX MobileNet or signal-fallback)
  ↓
screenshot / document / diagram?
  ├─ yes → OCR + text-LLM  ───────► DONE (~10× cheaper than vision)
  └─ no  → batch by category → vision inference with per-category token budget
```

Each stage is designed to **terminate early** whenever possible.

## Cost optimization, quantified

| technique | typical savings |
|---|---|
| heuristic skip (solid/icon) | 100% for that class |
| phash dedup + cache | 15–40% fewer API calls on real libraries |
| OCR + text-LLM for text-heavy images | 80–90% cheaper per image |
| per-category token budgets | 40–60% output token reduction |
| homogeneous batching | 20–35% input token reduction |
| resize to 768px + JPEG recompress | vision token cost ∝ image dimensions |
| cache on re-runs | near-zero repeat cost |

These multiply — real-world mixed libraries run **5–15× cheaper** than naive per-image vision calls.

## Package layout

```
labeldesk/
  core/
    config.py          YAML/TOML config with env-var overrides
    paths.py           ~/.labeldesk + cache dir management
    models/
      base.py          adapter ABC (vision + text inference)
      schema.py        configurable label field definitions
      registry.py      @register decorator, auto-discovery
      *_adapter.py     anthropic, openai, gemini, groq, lightning, ollama
    output/
      formatters.py    rename/csv/json/txt/preview + filename sanitization
    storage/
      job_store.py     SQLite job history
  pipeline/
    signals.py         free signal extraction (EXIF, pixel heuristics)
    hasher.py          perceptual hashing + dedup
    classifier.py      ONNX MobileNet or signal-based fallback
    normalizer.py      resize + JPEG compress for cheap vision tokens
    batcher.py         homogeneous batching + per-category budgets
    cache.py           phash-keyed SQLite result cache
    ocr.py             Tesseract wrapper
    runner.py          orchestrator — the decision tree lives here
  cli/main.py          Typer CLI
  tui/app.py           Textual terminal UI
  web/app.py           FastAPI backend
```

## Data directories

Everything lives under `~/.labeldesk/` (override with `LABELDESK_HOME`):

```
~/.labeldesk/
  config.toml
  .cache/
    labeldesk_cache.db     phash → result cache
    jobs.db                job history
    uploads/               web-uploaded images
```
