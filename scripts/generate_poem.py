from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
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
MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "320"))
MAX_ATTEMPTS = int(os.getenv("DEEPSEEK_MAX_ATTEMPTS", "3"))
AVOID_PEAK_PRICING = os.getenv("DEEPSEEK_AVOID_PEAK_PRICING", "true").lower() not in {
    "0",
    "false",
    "no",
}
MEMORY_RECENT_LIMIT = int(os.getenv("POEM_MEMORY_RECENT_LIMIT", "24"))
MEMORY_DUPLICATE_LIMIT = int(os.getenv("POEM_MEMORY_DUPLICATE_LIMIT", "16"))
MEMORY_KEYWORD_LIMIT = int(os.getenv("POEM_MEMORY_KEYWORD_LIMIT", "24"))
MEMORY_TITLE_LIMIT = int(os.getenv("POEM_MEMORY_TITLE_LIMIT", "160"))
PUERTO_RICO_TZ = timezone(timedelta(hours=-4))
BEIJING_TZ = timezone(timedelta(hours=8))
DEEPSEEK_PEAK_WINDOWS_BEIJING = ((9, 12), (14, 18))
NON_THINKING_CONFIG = {"type": "disabled"}
OUTPUT_DIR = Path("src/ai_poems")


SPANISH_STOPWORDS = {
    "abrir",
    "cada",
    "como",
    "con",
    "cuando",
    "del",
    "desde",
    "donde",
    "entre",
    "esta",
    "este",
    "hasta",
    "las",
    "los",
    "mas",
    "para",
    "pero",
    "por",
    "que",
    "sin",
    "sus",
    "una",
    "uno",
    "unos",
}


PROMPT_INSTRUCTIONS = """
Eres el poeta diario de luismarrero.me.

Escribe un poema breve, original y en español sobre la programación.

Reglas:
- Comienza con un título único, seguido por una línea en blanco, y luego el poema.
- No incluyas introducciones, despedidas, explicaciones, listas ni Markdown.
- Evita los títulos genéricos como "Algoritmo Poético", "Algoritmo del Alma" y variantes obvias.
- No repitas metáforas centrales de poemas recientes.
- Prefiere una imagen concreta, una escena pequeña o una tensión emocional distinta.
- Mantén el poema entre 4 y 14 versos.

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


POEM_ANGLES = [
    "un error mínimo que cambia la noche",
    "la ternura de un programa sencillo",
    "una variable que guarda algo que no cabe en memoria",
    "el silencio posterior a un build exitoso",
    "un commit pequeño que ordena el día",
    "la consola como diario íntimo",
    "un algoritmo que aprende a renunciar",
    "la paciencia de depurar sin prisa",
    "un archivo nuevo antes de saber qué decir",
    "la frontera entre automatizar y cuidar",
    "un test que protege una promesa",
    "la rareza de escribir instrucciones para una máquina",
]


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


@dataclass(frozen=True)
class DeepSeekResult:
    content: str
    usage: dict[str, int]


@dataclass(frozen=True)
class PoemMemory:
    recent_poems: list[dict[str, object]]
    repeated_titles: list[str]
    common_keywords: list[str]
    title_blacklist: list[str]


@dataclass(frozen=True)
class PoemGeneration:
    result: DeepSeekResult | None
    fallback_reason: str | None
    rejected_titles: list[str]


def is_deepseek_peak_pricing_time(now: datetime | None = None) -> bool:
    checked_at = now or datetime.now(timezone.utc)
    beijing_now = checked_at.astimezone(BEIJING_TZ)
    current_minutes = beijing_now.hour * 60 + beijing_now.minute

    return any(
        (start_hour * 60) <= current_minutes < (end_hour * 60)
        for start_hour, end_hour in DEEPSEEK_PEAK_WINDOWS_BEIJING
    )


def should_skip_deepseek_for_peak_pricing(now: datetime | None = None) -> bool:
    return AVOID_PEAK_PRICING and is_deepseek_peak_pricing_time(now)


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_title.lower()).strip()


def load_existing_poems(output_dir: Path = OUTPUT_DIR) -> list[dict[str, str]]:
    if not output_dir.exists():
        return []

    poems = []
    for file_path in sorted(output_dir.glob("*.json")):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        date = data.get("date")
        title = data.get("title")
        poem = data.get("poem")
        if isinstance(date, str) and isinstance(title, str) and isinstance(poem, str):
            poems.append({"date": date, "title": title, "poem": poem})

    return sorted(poems, key=lambda item: item["date"])


def is_repeated_title(title: str, existing_poems: list[dict[str, str]]) -> bool:
    title_key = normalize_title(title)
    return any(normalize_title(poem["title"]) == title_key for poem in existing_poems)


def poem_lines(poem: str) -> list[str]:
    return [line.strip() for line in poem.splitlines() if line.strip()]


def first_poem_line(poem: str) -> str:
    lines = poem_lines(poem)
    return lines[0] if lines else ""


def extract_keywords(text: str, limit: int = 6) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    words = re.findall(r"[a-z0-9]{4,}", ascii_text)
    counts = Counter(
        word for word in words if word not in SPANISH_STOPWORDS and not word.isdigit()
    )
    return [word for word, _count in counts.most_common(limit)]


def frequent_titles(
    existing_poems: list[dict[str, str]],
    limit: int = MEMORY_DUPLICATE_LIMIT,
) -> list[str]:
    titles_by_key = {}
    title_counts = Counter()

    for poem in existing_poems:
        key = normalize_title(poem["title"])
        if not key:
            continue
        title_counts[key] += 1
        titles_by_key.setdefault(key, poem["title"])

    repeated = [
        (titles_by_key[key], count) for key, count in title_counts.items() if count > 1
    ]
    repeated.sort(key=lambda item: (-item[1], item[0]))
    return [title for title, _count in repeated[:limit]]


def unique_recent_titles(
    existing_poems: list[dict[str, str]],
    limit: int = MEMORY_TITLE_LIMIT,
) -> list[str]:
    titles = []
    seen = set()

    for poem in reversed(existing_poems):
        key = normalize_title(poem["title"])
        if not key or key in seen:
            continue
        seen.add(key)
        titles.append(poem["title"])
        if len(titles) >= limit:
            break

    return titles


def build_poem_memory(existing_poems: list[dict[str, str]]) -> PoemMemory:
    recent_poems = []
    for poem in existing_poems[-MEMORY_RECENT_LIMIT:]:
        recent_poems.append(
            {
                "date": poem["date"],
                "title": poem["title"],
                "opening": first_poem_line(poem["poem"]),
                "keywords": extract_keywords(
                    f"{poem['title']}\n{poem['poem']}",
                    limit=5,
                ),
            }
        )

    common_keywords = extract_keywords(
        "\n".join(f"{poem['title']}\n{poem['poem']}" for poem in existing_poems),
        limit=MEMORY_KEYWORD_LIMIT,
    )
    repeated_titles = frequent_titles(existing_poems)
    title_blacklist = unique_recent_titles(existing_poems)

    for title in repeated_titles:
        if title not in title_blacklist:
            title_blacklist.append(title)

    return PoemMemory(
        recent_poems=recent_poems,
        repeated_titles=repeated_titles,
        common_keywords=common_keywords,
        title_blacklist=title_blacklist[:MEMORY_TITLE_LIMIT],
    )


def select_poem_angle(target_date: str, attempt: int) -> str:
    try:
        day_index = datetime.strptime(target_date, "%Y-%m-%d").toordinal()
    except ValueError:
        day_index = 0
    return POEM_ANGLES[(day_index + attempt - 1) % len(POEM_ANGLES)]


def build_poem_prompt(
    existing_poems: list[dict[str, str]],
    target_date: str,
    attempt: int = 1,
    rejected_titles: list[str] | None = None,
    force_distinct_title: bool = False,
) -> str:
    memory = build_poem_memory(existing_poems)
    rejected_titles = rejected_titles or []

    memory_lines = [
        PROMPT_INSTRUCTIONS,
        "",
        "Memoria para diversidad:",
        f"- Fecha objetivo: {target_date}.",
        f"- Enfoque sugerido para este intento: {select_poem_angle(target_date, attempt)}.",
    ]

    if memory.common_keywords:
        memory_lines.append(
            "- Palabras/imagenes ya muy usadas; evita apoyarte en ellas: "
            + "; ".join(memory.common_keywords)
            + "."
        )

    if memory.repeated_titles:
        memory_lines.append(
            "- Títulos frecuentes prohibidos: "
            + "; ".join(memory.repeated_titles)
            + "."
        )

    if memory.recent_poems:
        memory_lines.append("- Poemas recientes que no debes imitar:")
        for poem in memory.recent_poems:
            keywords = poem.get("keywords") or []
            keyword_text = ", ".join(str(keyword) for keyword in keywords)
            opening = str(poem.get("opening") or "")
            memory_lines.append(
                f"  - {poem['date']}: {poem['title']} | "
                f"apertura: {opening} | keywords: {keyword_text}"
            )

    if rejected_titles:
        memory_lines.append(
            "- Títulos rechazados en intentos anteriores: "
            + "; ".join(rejected_titles)
            + "."
        )

    if force_distinct_title:
        memory_lines.extend(
            [
                "",
                "Modo anti-repetición estricto:",
                "- No uses exactamente ninguno de estos títulos ya existentes:",
                "  " + "; ".join(memory.title_blacklist),
                "- Si tu primer título se parece a uno de la lista, descártalo.",
                "- El título debe tener una imagen concreta y una palabra inesperada.",
                "- Prohibidos títulos con 'Algoritmo', 'Código', 'Lenguaje' o 'Máquina'.",
            ]
        )

    memory_lines.append("")
    memory_lines.append("Responde solo con el título, una línea en blanco y el poema.")
    return "\n".join(memory_lines)


class DeepSeekAPI:
    def __init__(self, api_key: str | None, url: str, model: str):
        self.api_key = api_key
        self.url = url
        self.model = model

    def call(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int = MAX_TOKENS,
    ) -> DeepSeekResult | None:
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
            "max_tokens": max_tokens,
            "thinking": NON_THINKING_CONFIG,
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
            usage = {
                key: value
                for key, value in res_json.get("usage", {}).items()
                if isinstance(value, int)
            }
            return DeepSeekResult(
                content=res_json["choices"][0]["message"]["content"],
                usage=usage,
            )
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


def build_poem_data(raw_poem: str | None, date: str | None = None) -> dict[str, str]:
    model = MODEL if raw_poem else "fallback"
    title, poem = parse_poem(raw_poem or FALLBACK_POEM)

    return {
        "model": model,
        "date": date or poem_date(),
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


def generate_poem_with_memory(
    deepseek_api: DeepSeekAPI,
    existing_poems: list[dict[str, str]],
    target_date: str,
) -> PoemGeneration:
    rejected_titles = []

    if should_skip_deepseek_for_peak_pricing():
        print(
            "Skipping DeepSeek call during configured peak pricing window; "
            "using fallback poem."
        )
        return PoemGeneration(
            result=None,
            fallback_reason="peak_pricing_window",
            rejected_titles=rejected_titles,
        )

    for attempt in range(1, MAX_ATTEMPTS + 2):
        force_distinct_title = attempt > MAX_ATTEMPTS
        prompt = build_poem_prompt(
            existing_poems=existing_poems,
            target_date=target_date,
            attempt=attempt,
            rejected_titles=rejected_titles,
            force_distinct_title=force_distinct_title,
        )
        result = deepseek_api.call(
            prompt=prompt,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        if result is None:
            return PoemGeneration(
                result=None,
                fallback_reason="deepseek_unavailable",
                rejected_titles=rejected_titles,
            )

        title, _poem = parse_poem(result.content)
        if not is_repeated_title(title, existing_poems):
            return PoemGeneration(
                result=result,
                fallback_reason=None,
                rejected_titles=rejected_titles,
            )

        rejected_titles.append(title)
        print(f"Rejected repeated poem title on attempt {attempt}: {title}")

    print("All generated poem titles were repeated; using fallback poem.")
    return PoemGeneration(
        result=None,
        fallback_reason="repeated_titles",
        rejected_titles=rejected_titles,
    )


def main() -> None:
    target_date = poem_date()
    existing_poems = load_existing_poems()
    deepseek_api = DeepSeekAPI(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL)
    generation = generate_poem_with_memory(
        deepseek_api=deepseek_api,
        existing_poems=existing_poems,
        target_date=target_date,
    )
    raw_poem = generation.result.content if generation.result else None
    poem_data = build_poem_data(raw_poem, date=target_date)
    file_path = save_poem(poem_data)
    print(f"Saved poem to {file_path}")

    # Write execution status to metadata file
    metadata = {
        "success": generation.result is not None,
        "fallback_reason": generation.fallback_reason,
        "date": poem_data["date"],
        "title": poem_data["title"],
        "model": poem_data["model"],
        "thinking": NON_THINKING_CONFIG,
        "peak_pricing_guard_enabled": AVOID_PEAK_PRICING,
        "rejected_titles": generation.rejected_titles,
        "usage": generation.result.usage if generation.result else {},
    }

    metadata_path = Path("run_status.json")
    try:
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Saved run status to {metadata_path}")
    except OSError as error:
        print(f"Warning: Could not save run status to {metadata_path}: {error}")


if __name__ == "__main__":
    main()
