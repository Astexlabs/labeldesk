# HTTP API

Served by `labeldesk web` on port `7432` (configurable).

| method | path | description |
|---|---|---|
| GET | `/api/health` | liveness check |
| GET | `/api/models` | list adapters + availability |
| GET | `/api/config` | current config (keys masked) |
| POST | `/api/config` | set one key `{section, key, value}` |
| POST | `/api/upload` | multipart image upload → returns file IDs |
| POST | `/api/jobs` | create a labeling job (runs in background) |
| GET | `/api/jobs` | list jobs |
| GET | `/api/jobs/{id}` | job status + results |
| DELETE | `/api/jobs/{id}` | remove a job record |

## Create a job

```bash
curl -X POST http://localhost:7432/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "paths": ["/imgs"],
    "model": "groq",
    "fields": "dataset",
    "output": "json",
    "recursive": true
  }'
```

Poll `/api/jobs/{id}` for progress; `status` becomes `done` with a `results` dict.
