---
layout: home
hero:
  name: labeldesk
  text: Smart image labeling
  tagline: A cascading AI pipeline that treats vision models as a last resort, not a first call. Label thousands of images 5–15× cheaper than naive per-image inference.
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: CLI Reference
      link: /reference/cli
features:
  - title: Cascading cost optimization
    details: Free heuristics → perceptual-hash cache → local OCR → text LLM → vision. Every image takes the cheapest path that produces a good label.
  - title: Six providers out of the box
    details: Anthropic, OpenAI, Gemini, Groq, Lightning AI, and local Ollama — all behind one adapter interface. Switch with a single config key.
  - title: Configurable label schema
    details: Ask for exactly the fields you need — tags, dominant colors, quality score, detected objects, OCR text, confidence — per job, returned as structured JSON.
  - title: Three front-ends, one pipeline
    details: CLI for scripts, TUI for interactive runs, web dashboard for teams. Same cache, same job history.
---
