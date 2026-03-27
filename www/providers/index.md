# Providers

labeldesk ships with six vision backends behind a single adapter interface. Switch between them with `labeldesk config set default.model NAME` or `--model NAME` per-run.

| provider | default model | needs | best for |
|---|---|---|---|
| [Anthropic](/providers/anthropic) | claude-haiku-4-5 | API key | balanced quality/cost default |
| [OpenAI](/providers/openai) | gpt-4o-mini | API key | widest ecosystem compat |
| [Gemini](/providers/gemini) | gemini-1.5-flash | API key | cheapest cloud option |
| [Groq](/providers/groq) | llama-3.2-11b-vision | API key | fastest inference, very cheap |
| [Lightning AI](/providers/lightning) | user-deployed | API key + host | self-hosted OpenAI-compat endpoint |
| [Ollama](/providers/ollama) | llava | local host | zero-cost, offline, needs GPU |

## Check readiness

```bash
labeldesk models list
```

```
  ●  Claude (Anthropic)   claude-haiku-4-5-20251001   ready
     GPT (OpenAI)         gpt-4o-mini                 ✗ no key
     Gemini (Google)      gemini-1.5-flash            ✗ no key
     Groq                 llama-3.2-11b-vision        ready
     Lightning AI         lightning-vision            ✗ no key
     Ollama (local)       llava                       ✗ unreachable
```

## Test a single provider

```bash
labeldesk models test groq
```

## Pick interactively

```bash
labeldesk models pick
```

Walks you through choosing a default, entering its key, and picking a model ID.
