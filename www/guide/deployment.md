# Deployment

## Docker Compose

```bash
docker compose up                     # labeldesk API + Ollama
docker compose --profile frontend up  # + Next.js dashboard
```

The stack:
- `labeldesk` — API on `:7432`, data volume at `/data`
- `ollama` — local LLM on `:11434`, auto-wired as the default provider
- `web` (profile) — Next.js dev server on `:3000`

Drop images in `./imgs` and they mount read-only at `/imgs`.

## Environment variables

Every config key can be overridden:

```bash
LABELDESK_DEFAULT_MODEL=groq
LABELDESK_GROQ_API_KEY=gsk_...
LABELDESK_DEFAULT_FIELDS=dataset
```

Format: `LABELDESK_<SECTION>_<KEY>` (uppercase, underscores).

## Releasing to PyPI

Tag-triggered — no accidental publishes:

```bash
# bump version in pyproject.toml
git commit -am "release: v0.3.0"
git tag v0.3.0
git push origin main --tags
```

The `.github/workflows/publish.yml` workflow verifies the tag is on `main`, runs tests, checks the version matches, builds, and publishes via OIDC trusted publishing.
