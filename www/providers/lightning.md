# Lightning AI

Lightning AI Studios let you deploy any open-weight vision model behind an **OpenAI-compatible** HTTP endpoint. labeldesk talks to it over the standard `/v1/chat/completions` API — no SDK required.

This is the right provider when you want **full control over the model** (fine-tuned checkpoints, custom LLaVA variants, private deployments) while keeping labeldesk's pipeline unchanged.

## Setup

1. Deploy a vision model in a Lightning Studio and expose it as an OpenAI-compatible server (e.g. with LitServe or vLLM)
2. Grab the Studio URL and an API key from the Lightning dashboard

```bash
labeldesk config set lightning.host https://8000-01hxxx.cloudspaces.litng.ai
labeldesk config set lightning.api_key lai_...
labeldesk config set lightning.model_id llava-1.6-34b
labeldesk config set default.model lightning
```

## Config

```yaml
lightning:
  api_key: lai_...
  host: https://8000-01hxxx.cloudspaces.litng.ai
  model_id: llava-1.6-34b
  max_tokens: 300
```

Both `api_key` **and** `host` are required — the adapter reports not-ready if either is missing.

## Verify

```bash
labeldesk models test lightning
```

## Notes

- Zero extra Python dependencies — uses stdlib `urllib`
- Works with any server that speaks OpenAI's chat-completions vision format
- Cost fields in labeldesk are estimates; actual billing depends on your Studio config
