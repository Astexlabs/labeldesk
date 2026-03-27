# Groq

Groq runs open-weight models on custom LPU hardware — **inference is absurdly fast** and pricing is among the lowest of any hosted provider. Ideal for high-volume labeling jobs where latency matters.

## Setup

Get a key at [console.groq.com](https://console.groq.com). There's a free tier.

```bash
labeldesk config set groq.api_key gsk_...
labeldesk config set default.model groq
```

Or via env:

```bash
export LABELDESK_GROQ_API_KEY=gsk_...
```

## Config

```yaml
groq:
  api_key: gsk_...
  model_id: llama-3.2-11b-vision-preview
  max_tokens: 300
```

## Supported models

Any Groq vision model works — set `model_id` to the one you want:

- `llama-3.2-11b-vision-preview` (default — fast, cheap)
- `llama-3.2-90b-vision-preview` (better for nuanced labels)

## Verify

```bash
labeldesk models test groq
```

## Notes

- Uses the official `groq` Python SDK (installed via `uv sync --extra ai`)
- OpenAI-compatible chat format under the hood
- Good choice for `--fields full` runs — the extra tokens barely register on cost
