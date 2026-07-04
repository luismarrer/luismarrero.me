# Luis Marrero González – Personal Website

[![Website](https://img.shields.io/badge/site-luismarrero.me-0f172a?style=for-the-badge)](https://www.luismarrero.me/)

This is my personal site built with [Astro](https://astro.build).  
I use it to experiment with ideas, explore creative tools, and connect my projects.

This site is based on a template created by [Kadir Lofca](https://github.com/kadirlofca), who deserves all the credit for the design and structure. I've adapted it for my experiments.

If you're looking for my resume and portfolio, visit [luismarrer.github.io/en](https://luismarrer.github.io/en/).

## Development

Use pnpm for the Astro site:

```sh
pnpm install
pnpm dev
pnpm build
```

The Markdown Regex Editor calls `https://markdown-regex.vercel.app/parse` in production. During local development, Astro proxies `/api/markdown-parse` to a parser server so the browser can avoid localhost CORS issues. By default it expects the parser repo at `http://127.0.0.1:8000`; set `MARKDOWN_PARSER_TARGET` to point somewhere else.

## 🧪 Experiments

### Python

- [AI Poems](https://www.luismarrero.me/) — Daily poetry generated using AI API (DeepSeek), automatically committed with GitHub Actions.

#### Working on the poem generator

The Python tools are declared in `pyproject.toml`. Use `uv` locally:

```sh
uv sync --dev
uv run python scripts/generate_poem.py
uv run pytest
uv run ruff check scripts tests
uv run ruff format scripts tests
```

Set `DEEPSEEK_API_KEY` in `.env` for local generation. You can override the model with `DEEPSEEK_MODEL`, cap output with `DEEPSEEK_MAX_TOKENS`, tune retries with `DEEPSEEK_MAX_ATTEMPTS`, and adjust prompt memory with `POEM_MEMORY_RECENT_LIMIT`, `POEM_MEMORY_DUPLICATE_LIMIT`, `POEM_MEMORY_KEYWORD_LIMIT`, and `POEM_MEMORY_TITLE_LIMIT`. When API usage metadata is available, the notification step prints estimated cost, DeepSeek USD balance, and approximate poems remaining to the workflow logs. If generation fails or repeats titles too many times, the fallback poem is still published so the site does not miss a day.

Optional WhatsApp notifications use `CALLMEBOT_PHONE` and `CALLMEBOT_APIKEY` for personal CallMeBot messages. The message includes whether the poem was generated successfully or the fallback was used, token counts, estimated DeepSeek cost, current balance, and approximate poems remaining.

- [Markdown Regex Editor](https://www.luismarrero.me/markdown-live) — A Markdown editor built using Regex.

## ✅ TODOs

- [x] Mejorar diversidad del poeta con memoria rica de poemas anteriores, retry de títulos repetidos, prompt estricto anti-repetición, `max_tokens` y thinking desactivado.
- [x] Enviar por WhatsApp el estado de generación, costo del poema diario, balance restante de DeepSeek y estimado de poemas disponibles.
- [ ] Crear un monitor que avise cambios en pricing y modelos de DeepSeek.

---

Feel free to explore, fork, or reach out.
