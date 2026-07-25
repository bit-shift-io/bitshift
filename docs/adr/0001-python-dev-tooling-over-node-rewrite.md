# ADR 0001: Keep local dev tooling in Python rather than rewriting the site build in Node/TypeScript

**Status:** Accepted
**Date:** 2026-07-25

## Context

Local testing required a manual `edit → tools/build.py → tools/localhost.sh` loop, and `tools/localhost.sh` (a plain `python3 -m http.server`) doesn't replicate Firebase Hosting's `cleanUrls: true` behavior, so every page except the homepage 404s locally unless `.html` is typed manually. Node-based tooling (e.g. Vite, browser-sync, Eleventy) solves hot-reload and clean-URL dev serving largely out of the box, which raised the question of whether to move the whole site build off `staticjinja`/Jinja2 onto a Node/TypeScript stack to get that tooling for free.

## Decision

Stay on Python. Build a small, purpose-built `tools/dev.py` that reuses the existing `staticjinja`/Jinja2 build (`tools/build.py`) and adds: file watching (`watchdog`), clean-URL resolution in a custom stdlib HTTP handler, and browser live-reload via a polling-based injected script. No template or build-pipeline rewrite.

## Alternatives Considered

- **Rewrite templates and build pipeline in Node/TypeScript (e.g. Vite or Eleventy):** would give hot-reload and clean URLs near-for-free, but requires rewriting all ~10 Jinja2 templates into a JS templating language, reimplementing `build.py`'s render logic, and introducing a second toolchain (npm/node) alongside the existing pip-based one. Rejected: the actual problem is a missing local dev loop, not a deficiency in Jinja2/staticjinja — a full rewrite is a large, high-risk change to a site that currently works, for no functional gain on the deployed site itself.

## Consequences

- New dependency `watchdog` added to `requirements.txt`; no other new toolchain (no Node/npm) introduced.
- `tools/build.py`'s render logic is reused by `tools/dev.py` rather than duplicated, keeping a single source of truth for how templates render.
- If browser-native tooling needs (bundling, JS module imports, etc.) grow significantly in the future, this decision may need revisiting — but that's out of scope for the current site, which has no JS build step today.
- Live-reload latency is bounded by a ~1s polling interval rather than instant websocket push, a deliberate trade-off to avoid a second new dependency (see DECISIONS.md in `.scratch/local-dev-server/` for the full reasoning, captured here since the substance is what matters going forward).
