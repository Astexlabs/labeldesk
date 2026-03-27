# Installation

## Requirements

- Python **3.13+**
- Optional: `tesseract-ocr` for the OCR path
- Optional: Node.js 18+ for the web dashboard frontend

## pip

```bash
pip install labeldesk
```

## uv (recommended for development)

```bash
git clone https://github.com/Astexlabs/labeldesk
cd labeldesk
uv sync
```

### Optional extras

| extra | installs | when you need it |
|---|---|---|
| `ai` | anthropic, openai, google-generativeai, groq SDKs | using any cloud provider |
| `onnx` | onnxruntime | local image classifier (otherwise falls back to signal heuristics) |
| `dev` | pytest | running tests |

```bash
uv sync --extra ai --extra onnx
```

## Docker

```bash
docker compose up                     # labeldesk API + Ollama
docker compose --profile frontend up  # + Next.js dashboard on :3000
```

Images dropped in `./imgs` are mounted read-only at `/imgs` inside the container.

## One-liner setup

```bash
./setup.sh
```

Installs uv if missing, syncs deps, seeds config, runs tests, and offers to launch the TUI.

## Verify

```bash
labeldesk models list
```

You should see all six providers listed with their readiness status.
