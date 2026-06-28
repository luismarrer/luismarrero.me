from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
TEMPERATURE = 0.8
PUERTO_RICO_TZ = timezone(timedelta(hours=-4))
OUTPUT_DIR = Path("src/ai_poems")


PROMPT = """
Escribe un poema breve y original sobre la programación.

Debe comenzar con un título, seguido por una línea en blanco, y luego el poema. No incluyas introducciones, despedidas ni explicaciones. Solo el poema.

Ejemplo de respuesta:

Código y Verso

Eres lógica pura,
estructura clara,
sintaxis precisa
que el mundo declara.

Cada línea un paso,
cada error, enseñanza,
y al fin, cuando compila,
¡qué dulce es la recompensa!

Un bucle de ideas,
un if en la mente,
la máquina obedece
cuando el código es coherente.
""".strip()


FALLBACK_POEM = """
Bitácora del Código

La pantalla respira
su pulso de cristal,
una función despierta
con ritmo decimal.

Si el error se presenta,
lo escucho sin temor;
depuro la pregunta
hasta encontrar su flor.
""".strip()


class DeepSeekAPI:
    def __init__(self, api_key: str | None, url: str, model: str):
        self.api_key = api_key
        self.url = url
        self.model = model

    def call(self, prompt: str, temperature: float) -> str | None:
        if not self.api_key:
            print("DEEPSEEK_API_KEY is not set; using fallback poem.")
            return None

        try:
            import requests
        except ImportError:
            print("requests is not installed; using fallback poem.")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        try:
            response = requests.post(
                self.url,
                json=data,
                headers=headers,
                timeout=120,
            )
            response.raise_for_status()
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError, ValueError) as error:
            print(f"Error generating poem: {error}")
            return None


def poem_date() -> str:
    tomorrow = datetime.now(PUERTO_RICO_TZ) + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


def parse_poem(raw_poem: str) -> tuple[str, str]:
    lines = [line.rstrip() for line in raw_poem.strip().splitlines()]
    lines = [line for line in lines if line.strip()]

    if len(lines) < 2:
        return "Poema del día", raw_poem.strip()

    title = lines[0].strip()
    while title.startswith("#"):
        title = title[1:].strip()
    title = title.strip("*").strip()

    body = "\n".join(lines[1:]).strip()
    return title or "Poema del día", body or raw_poem.strip()


def build_poem_data(raw_poem: str | None) -> dict[str, str]:
    model = MODEL if raw_poem else "fallback"
    title, poem = parse_poem(raw_poem or FALLBACK_POEM)

    return {
        "model": model,
        "date": poem_date(),
        "title": title,
        "poem": poem,
    }


def save_poem(poem_data: dict[str, str]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / f"{poem_data['date']}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(poem_data, file, indent=2, ensure_ascii=False)
        file.write("\n")

    return file_path


def main() -> None:
    deepseek_api = DeepSeekAPI(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL)
    raw_poem = deepseek_api.call(prompt=PROMPT, temperature=TEMPERATURE)
    poem_data = build_poem_data(raw_poem)
    file_path = save_poem(poem_data)
    print(f"Saved poem to {file_path}")


if __name__ == "__main__":
    main()
