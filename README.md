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

Set `DEEPSEEK_API_KEY` in `.env` for local generation. You can override the model with `DEEPSEEK_MODEL`.

- [Markdown Regex Editor](https://www.luismarrero.me/markdown-live) — A Markdown editor built using Regex.

## ✅ TODOs

- [X] Añadir luismarrer.github.io/en en la web
- [ ] Arreglar la arquitectura de los poemas. Para que no explote.
- [ ] Hacer paginación en los poemas. Quizás tambien en los posts.
- [ ] Mejorar poeta, mostrar costo? Hacerlo más barato? Hacerlo más diverso, no repita titulos, que aprenda de poemas anteriores?
- [X] Añadir tests
- [ ] Terminar los blogs.
- [ ] Eliminar boton de ver todos los poemas
- [ ] Mejorar SEO, que aparezca en Google.

---

Feel free to explore, fork, or reach out.
