# Ollama

Run vision models **locally** — zero API cost, works offline, no data leaves your machine.

## Setup

Install from [ollama.com](https://ollama.com), then pull a vision model:

```bash
ollama pull llava
```

Point labeldesk at it:

```bash
labeldesk config set ollama.host http://localhost:11434
labeldesk config set default.model ollama
```

## Config

```yaml
ollama:
  host: http://localhost:11434
  model_id: llava          # or bakllava, llava:13b, moondream, etc.
  max_tokens: 300
```

## Verify

```bash
labeldesk models test ollama
```

## Notes

- Needs a GPU with enough VRAM for the model (llava:7b ≈ 6GB)
- The Docker Compose stack wires Ollama up automatically
- Slower than cloud providers but perfectly free
