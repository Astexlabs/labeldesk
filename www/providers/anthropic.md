# Anthropic

Claude's vision models are the default — good quality at low Haiku pricing.

## Setup

Get a key at [console.anthropic.com](https://console.anthropic.com).

```bash
labeldesk config set anthropic.api_key sk-ant-...
labeldesk config set default.model anthropic
```

Or via env:

```bash
export LABELDESK_ANTHROPIC_API_KEY=sk-ant-...
```

## Config

```yaml
anthropic:
  api_key: sk-ant-...
  model_id: claude-haiku-4-5-20251001   # or claude-sonnet-4-6 for harder images
  max_tokens: 300
```

## Notes

- Haiku is plenty for titles/tags; bump to Sonnet for nuanced descriptions
- The adapter uses both vision and text-only paths (text is cheaper for OCR-summarized content)
