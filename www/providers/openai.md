# OpenAI

## Setup

Get a key at [platform.openai.com](https://platform.openai.com).

```bash
labeldesk config set openai.api_key sk-...
labeldesk config set default.model openai
```

## Config

```yaml
openai:
  api_key: sk-...
  model_id: gpt-4o-mini
  max_tokens: 300
```

## Notes

- `gpt-4o-mini` is the right choice for bulk labeling — cheap and fast
- Images are sent at `detail: low` to minimize token usage
