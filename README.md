# Luis Marrero – Personal Website

[![Website](https://img.shields.io/badge/site-luismarrero.me-0f172a?style=for-the-badge)](https://www.luismarrero.me/)

This is my personal site built with [Astro](https://astro.build).  
I use it to experiment with ideas, explore creative tools, and connect my projects.

This site is based on a template created by [Kadir Lofca](https://github.com/kadirlofca), who deserves all the credit for the design and structure. I've adapted it for my experiments.

If you're looking for my resume and portfolio, visit [luismarrer.github.io/en](https://luismarrer.github.io/en/).

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

- [Markdown Regex Editor](https://www.luismarrero.me/markdown-live) — A Markdown editor built using Regex. The parser is deployed on Railway.

## ✅ TODOs

- [ ] Add more markdown features
- [ ] Fix newline, tabs and spaces handling in Markdown editor

---

Feel free to explore, fork, or reach out.
