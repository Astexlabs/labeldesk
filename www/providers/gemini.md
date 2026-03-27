# Google Gemini

Cheapest of the cloud options.

## Setup

Get a key at [aistudio.google.com](https://aistudio.google.com).

```bash
labeldesk config set gemini.api_key AIza...
labeldesk config set default.model gemini
```

## Config

```yaml
gemini:
  api_key: AIza...
  model_id: gemini-1.5-flash
  max_tokens: 300
```

## Notes

- Flash has a generous free tier — great for experimenting
- Requires the `ai` extra: `uv sync --extra ai`
