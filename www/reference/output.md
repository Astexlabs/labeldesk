# Output Formats

Control with `--output FMT` (and `--out-dir PATH` where applicable).

## `preview` (default)

Prints one line per image to stdout. No writes.

```
IMG_4201.jpg: golden retriever on beach [vision-generic]
IMG_4202.jpg: beach sunset landscape [cache]
```

## `json`

Full result dict including every schema field. Writes `labels.json` to `--out-dir` or stdout.

## `csv`

Row-per-image. Writes `labels.csv`.

## `txt`

Human-readable blocks. Writes `labels.txt`.

## `rename`

Renames files **in place** using the sanitized title.

```
IMG_4201.jpg → golden-retriever-on-beach.jpg
```

## `copy-rename`

Same, but copies to `--out-dir` instead of touching originals.

## Filename rules

Titles are lowercased, non-word chars stripped, whitespace → dashes, max 80 chars. Collisions get a `-2`, `-3`, … suffix.
