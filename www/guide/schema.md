# Label Schema

By default labeldesk asks the model for a title. That's fine for renaming files, but useless if you're building a training dataset. The **schema system** lets you request exactly the structured fields you need, per job.

## Available fields

Run `labeldesk schema` to see the live list. As of the current release:

| field | type | returns |
|---|---|---|
| `title` | str | short descriptive title (3–6 words) |
| `desc` | str | one-sentence description |
| `tags` | list | 5–10 lowercase keyword tags |
| `dominant_colors` | list | 3–5 dominant color names |
| `content_type` | str | `photo` / `screenshot` / `diagram` / `icon` / `illustration` / `document` / `ui` / `meme` |
| `use_case` | str | inferred intent: `hero-image`, `thumbnail`, `avatar`, `documentation`, `social-post`, `product-shot`, … |
| `quality_score` | int | 1–10 rating for sharpness, lighting, composition |
| `suggested_fname` | str | clean kebab-case filename (no extension) |
| `ocr_text` | str | any text visible in the image, or `none` |
| `objects` | list | main objects/subjects detected |
| `scene` | str | scene context: indoor/outdoor/studio/abstract + setting |
| `confidence` | float | model's self-reported confidence, 0.0–1.0 |

## Presets

Rather than listing fields every time, use a preset:

| preset | fields |
|---|---|
| `basic` | title, desc |
| `dataset` | title, tags, content_type, objects, quality_score, confidence |
| `rename` | suggested_fname, content_type |
| `full` | everything |

## Usage

### Command-line

```bash
# preset
labeldesk label ./imgs --fields dataset --output json

# custom field list
labeldesk label ./imgs --fields title,tags,dominant_colors,quality_score
```

### Config default

Set it once and every job uses it:

```bash
labeldesk config set default.fields dataset
```

Or in `labeldesk.yaml`:

```yaml
default:
  fields: "title,tags,objects,quality_score"
```

## How it works

When `--fields` is set, the runner builds a **JSON-extraction prompt** tailored to exactly those fields, with a token budget sized to fit the expected response. The model returns structured JSON which is parsed, type-coerced (lists split on commas, scores cast to int/float), and stored in the result's `extra` dict.

Output as JSON to get the full structure:

```bash
labeldesk label ./pics --fields full --output json --out-dir ./out
```

```json
{
  "pics/IMG_4201.jpg": {
    "title": "golden retriever on beach",
    "tags": ["dog", "beach", "golden-retriever", "sunset", "sand"],
    "content_type": "photo",
    "objects": ["dog", "ocean", "sand"],
    "quality_score": 8,
    "dominant_colors": ["gold", "blue", "tan"],
    "confidence": 0.92,
    "src": "vision-generic"
  }
}
```
