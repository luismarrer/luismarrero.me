import json
import re

import scripts.generate_poem as generate_poem


def test_parse_poem_splits_title_and_body():
    title, body = generate_poem.parse_poem(
        "Código Claro\n\nPrimera línea\nSegunda línea"
    )

    assert title == "Código Claro"
    assert body == "Primera línea\nSegunda línea"


def test_parse_poem_handles_single_line_response():
    title, body = generate_poem.parse_poem("Solo una línea")

    assert title == "Poema del día"
    assert body == "Solo una línea"


def test_build_poem_data_uses_fallback_when_api_fails():
    poem_data = generate_poem.build_poem_data(None)

    assert poem_data["model"] == "fallback"
    assert poem_data["title"] == "Bitácora del Código"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", poem_data["date"])
    assert "La pantalla respira" in poem_data["poem"]


def test_save_poem_writes_schema_compatible_json(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_poem, "OUTPUT_DIR", tmp_path)
    poem_data = {
        "model": "test-model",
        "date": "2026-01-02",
        "title": "Test Poem",
        "poem": "Line one\nLine two",
    }

    file_path = generate_poem.save_poem(poem_data)

    assert file_path == tmp_path / "2026-01-02.json"
    assert json.loads(file_path.read_text(encoding="utf-8")) == poem_data


def test_deepseek_api_uses_fallback_without_key():
    api = generate_poem.DeepSeekAPI(api_key=None, url="https://example.com", model="x")

    assert api.call(prompt="hello", temperature=0.8) is None
