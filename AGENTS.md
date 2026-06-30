# Repository Guidelines

## Project Structure & Module Organization

This is an Astro personal site with Svelte islands. Main pages live in `src/pages`, reusable Astro components in `src/components`, and interactive Svelte components in `src/components/reactive`. Layout shell code is in `src/layouts`, shared stores in `src/stores`, Tailwind and helpers in `src/styles`, and JSON profile/site data in `src/data`.

Content collections are configured in `src/content.config.ts`. Blog posts are Markdown or MDX files under `src/posts`; AI poem entries are JSON files under `src/ai_poems` using date-like filenames such as `2026-06-11.json`. Static assets belong in `public`.

## Build, Test, and Development Commands

Use pnpm, matching the checked-in `pnpm-lock.yaml`.

- `pnpm install`: install dependencies.
- `pnpm dev`: start the Astro dev server.
- `pnpm build`: build the production site and run Astro content/type validation.
- `pnpm preview`: preview the built site locally.
- `pnpm astro ...`: run Astro CLI commands directly, for example `pnpm astro check` if the check integration is added later.

Python tooling for the poem generator is managed with uv, matching `pyproject.toml` and `uv.lock`.

- `uv sync --dev`: install Python runtime and dev dependencies.
- `uv run python scripts/generate_poem.py`: generate an AI poem locally.
- `uv run pytest`: run Python tests.
- `uv run ruff check scripts tests`: lint Python tools and tests.
- `uv run ruff format scripts tests`: format Python tools and tests.

There is no dedicated JavaScript test script in this repository yet; run `pnpm build` before submitting site changes.

## Coding Style & Naming Conventions

Prefer TypeScript where applicable and keep Astro/Svelte imports using the `@/*` alias for `src/*`. Use two-space indentation in Svelte/TypeScript blocks and follow the existing Astro component formatting. Name components in PascalCase, stores as `*.store.ts`, and content files with readable kebab-case names.

Keep data files schema-compatible with `src/content.config.ts`: posts require `title`, `published`, `description`, `date`, and `tags`; poem JSON requires `model`, `title`, `date`, and `poem`.

## Testing Guidelines

For UI or content changes, validate with `pnpm build` and manually check affected pages through `pnpm dev` or `pnpm preview`. For Python poem-generator changes, run `uv run pytest` and `uv run ruff check scripts tests`; use `uv run ruff format scripts tests` when formatting is needed. If adding JavaScript tests later, colocate focused tests near the feature or use a clear `tests` directory.

## Commit & Pull Request Guidelines

The Git history is sparse, but existing commits use concise imperative phrasing, for example `Trigger rebuild for show 2026-06-23 poem`. Keep commits short and action-oriented.

Pull requests should describe the change, list validation performed, link related issues when available, and include screenshots for visible UI changes. Note content schema changes or generated poem updates explicitly.

## Security & Configuration Tips

Do not commit secrets or API keys. Set `DEEPSEEK_API_KEY` in `.env` for local poem generation only. The Markdown editor calls an external parser endpoint from the client in production and uses the local `/api/markdown-parse` dev proxy, so treat endpoint or proxy changes as user-visible behavior and document them in the PR.
