# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Luis Marrero González's personal site: an Astro site with Svelte islands, based on a template by Kadir Lofca. Two "experiments" live inside it: a daily AI-generated poem (Python, DeepSeek API) and a Markdown Regex Editor.

## Commands

Astro site (use pnpm, matching `pnpm-lock.yaml`):

```sh
pnpm install
pnpm dev        # start dev server
pnpm build      # production build; also runs Astro content/type validation
pnpm preview    # preview the production build
```

There is no dedicated JS test script — run `pnpm build` to validate site changes (it fails on content-schema or type errors).

Python tooling (poem generator), managed with `uv`:

```sh
uv sync --dev
uv run python scripts/generate_poem.py     # generate a poem locally
uv run pytest                              # run tests (single: uv run pytest tests/test_generate_poem.py::test_name)
uv run ruff check scripts tests            # lint
uv run ruff format scripts tests           # format
```

`DEEPSEEK_API_KEY` (and optional `DEEPSEEK_MODEL`) go in `.env` for local generation; without a key, `generate_poem.py` falls back to a hardcoded poem.

## Architecture

### Content collections (`src/content.config.ts`)

Two Astro content collections, both loaded via `glob`:
- **`posts`** — Markdown/MDX under `src/posts`, schema requires `title`, `published`, `description`, `date`, `tags`.
- **`ai_poems`** — JSON files under `src/ai_poems` named by date (e.g. `2026-06-11.json`), schema requires `model`, `title`, `date`, `poem`.

Keep new data files schema-compatible with these definitions.

### AI poem pipeline

`scripts/generate_poem.py` calls the DeepSeek chat completions API with a fixed Spanish-language prompt, parses the response into a title/body, and writes `src/ai_poems/<date>.json` (date = tomorrow in Puerto Rico time, since the workflow runs the evening before). Two GitHub Actions workflows drive this in production:
- `.github/workflows/generate-poem.yml` — runs nightly at 20:00 UTC, generates the poem, commits it to `src/ai_poems/`.
- `.github/workflows/rebuild-site.yml` — runs at 04:00 UTC, appends to `.update_log` and pushes, purely to trigger a rebuild/redeploy that picks up the poem committed a few hours earlier.

Poem pages are rendered at `src/pages/poems/index.astro` (archive) and `src/pages/poems/[date].astro` (single poem), backed by `src/components/Poems.astro`.

### Markdown Regex Editor

`src/pages/markdown-live.astro` renders Svelte components (`EditorPane`, `PreviewPane`, `MarkdownEditor` in `src/components/reactive`) that call an external regex-based Markdown parser at `https://markdown-regex.vercel.app/parse` in production. In dev, Astro's Vite server proxies `/api/markdown-parse` → `MARKDOWN_PARSER_TARGET` (default `http://127.0.0.1:8000`, i.e. a locally running parser repo) to sidestep browser CORS, rewriting the path to `/parse` (see `astro.config.mjs`). Treat changes to this endpoint or proxy as user-visible behavior worth calling out explicitly.

### Site structure

- `src/pages` — routes; `src/layouts/Layout.astro` is the shared shell.
- `src/components` — Astro components; `src/components/reactive` — Svelte islands (editor, tags/filters UI, menu).
- `src/stores/filters.store.ts` — nanostores state, e.g. for post/tag filtering (`Filters.svelte`, `Tags.svelte`).
- `src/data/*.json` — profile/site data (site config, contact, personal, professional) consumed by components/pages directly.
- Path alias `@/*` maps to `src/*`.
- `/posts` is the posts index (`src/pages/posts/index.astro`), listing published posts via the `Posts.svelte` island; individual posts render at `/posts/<slug>` (`src/pages/posts/[...slug].astro`).

## Conventions

- Two-space indentation in Svelte/TypeScript; PascalCase components; stores named `*.store.ts`; kebab-case content filenames.
- Commit messages: short, imperative (e.g. `Trigger rebuild for show 2026-06-23 poem`).
