# Getting Started

labeldesk is an image-labeling pipeline built around one idea: **AI inference is the most expensive thing you can do, so do it last.** Before a single token is spent, every image passes through free heuristics, a perceptual-hash dedup cache, local classification, and OCR. Only the images that genuinely need a vision model ever reach one.

## Quick install

```bash
pip install labeldesk
# or, from source
git clone https://github.com/Astexlabs/labeldesk
cd labeldesk && uv sync
```

## First run

Configure a provider (Groq is the fastest to try — free tier, instant signup):

```bash
labeldesk config set groq.api_key gsk_...
labeldesk config set default.model groq
```

Label a folder:

```bash
labeldesk label ./photos --output json --out-dir ./out
```

Or open the interactive TUI:

```bash
labeldesk
```

## What just happened

For each image, labeldesk:

1. Extracted EXIF, aspect ratio, dominant color, edge density — **free**
2. Checked if it's a solid color / icon → heuristic label, **skip AI**
3. Computed a perceptual hash → cache hit? **skip AI**
4. Classified locally (ONNX or signal-based) → screenshot/document? → **OCR + text LLM** (10× cheaper than vision)
5. Only if none of the above worked → batched vision inference with a per-category token budget

On a real mixed photo library, this typically cuts cost **5–15×** compared to sending every image straight to a vision endpoint.

## Next steps

- [Installation options](/guide/installation) — uv, Docker, optional extras
- [Label schema](/guide/schema) — get structured fields like `quality_score`, `objects`, `dominant_colors`
- [Provider setup](/providers/) — configure any of the six supported backends
- [CLI reference](/reference/cli) — every command and flag
