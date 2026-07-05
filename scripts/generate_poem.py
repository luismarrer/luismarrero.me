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
FALLBACK_REFILL_THRESHOLD = int(os.getenv("FALLBACK_POEM_REFILL_THRESHOLD", "7"))
FALLBACK_REFILL_TARGET = int(os.getenv("FALLBACK_POEM_REFILL_TARGET", "30"))
FALLBACK_REFILL_MAX_TOKENS = int(os.getenv("FALLBACK_POEM_REFILL_MAX_TOKENS", "5000"))
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
FALLBACK_BANK_PATH = Path("src/data/fallback-poems.json")


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


EMERGENCY_FALLBACK_POEM = """
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


def normalize_content(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", normalized.lower()).strip()


def fallback_poem_to_raw(fallback_poem: dict[str, str]) -> str:
    return f"{fallback_poem['title']}\n\n{fallback_poem['poem']}"


def fallback_poem_from_raw(raw_poem: str) -> dict[str, str]:
    title, poem = parse_poem(raw_poem)
    return {"title": title, "poem": poem}


def coerce_fallback_poem(value: object) -> dict[str, str] | None:
    if isinstance(value, str):
        return fallback_poem_from_raw(value)

    if not isinstance(value, dict):
        return None

    title = value.get("title")
    poem = value.get("poem")
    if not isinstance(title, str) or not isinstance(poem, str):
        return None

    title = title.strip()
    poem = poem.strip()
    if not title or not poem:
        return None

    return {"title": title, "poem": poem}


def unique_fallback_poems(fallback_poems: list[dict[str, str]]) -> list[dict[str, str]]:
    unique_poems = []
    seen_titles = set()
    seen_bodies = set()

    for fallback_poem in fallback_poems:
        title_key = normalize_title(fallback_poem["title"])
        body_key = normalize_content(fallback_poem["poem"])
        if not title_key or not body_key:
            continue
        if title_key in seen_titles or body_key in seen_bodies:
            continue
        seen_titles.add(title_key)
        seen_bodies.add(body_key)
        unique_poems.append(fallback_poem)

    return unique_poems


def load_fallback_poems(path: Path = FALLBACK_BANK_PATH) -> list[dict[str, str]]:
    try:
        raw_bank = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [fallback_poem_from_raw(EMERGENCY_FALLBACK_POEM)]

    if not isinstance(raw_bank, list):
        return [fallback_poem_from_raw(EMERGENCY_FALLBACK_POEM)]

    fallback_poems = [
        fallback_poem
        for value in raw_bank
        if (fallback_poem := coerce_fallback_poem(value)) is not None
    ]
    return unique_fallback_poems(fallback_poems) or [
        fallback_poem_from_raw(EMERGENCY_FALLBACK_POEM)
    ]


def save_fallback_poems(
    fallback_poems: list[dict[str, str]],
    path: Path = FALLBACK_BANK_PATH,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            unique_fallback_poems(fallback_poems), file, indent=2, ensure_ascii=False
        )
        file.write("\n")
    return path


def is_used_fallback_poem(
    fallback_poem: dict[str, str],
    existing_poems: list[dict[str, str]],
    target_date: str | None = None,
) -> bool:
    title_key = normalize_title(fallback_poem["title"])
    body_key = normalize_content(fallback_poem["poem"])

    for existing_poem in existing_poems:
        if target_date and existing_poem["date"] == target_date:
            continue
        if normalize_title(existing_poem["title"]) == title_key:
            return True
        if normalize_content(existing_poem["poem"]) == body_key:
            return True

    return False


def unused_fallback_poems(
    fallback_poems: list[dict[str, str]],
    existing_poems: list[dict[str, str]],
    target_date: str | None = None,
) -> list[dict[str, str]]:
    return [
        fallback_poem
        for fallback_poem in fallback_poems
        if not is_used_fallback_poem(fallback_poem, existing_poems, target_date)
    ]


def select_unused_fallback_poem(
    date: str | None = None,
    existing_poems: list[dict[str, str]] | None = None,
    fallback_poems: list[dict[str, str]] | None = None,
) -> dict[str, str]:
    target_date = date or poem_date()
    existing_poems = existing_poems or []
    if fallback_poems is None:
        fallback_poems = load_fallback_poems()
    available_poems = unused_fallback_poems(
        fallback_poems,
        existing_poems,
        target_date=target_date,
    )

    try:
        day_index = datetime.strptime(target_date, "%Y-%m-%d").toordinal()
    except ValueError:
        day_index = 0

    if available_poems:
        return available_poems[day_index % len(available_poems)]

    print("Warning: fallback poem bank is exhausted; using emergency fallback.")
    return fallback_poem_from_raw(EMERGENCY_FALLBACK_POEM)


def select_fallback_poem(
    date: str | None = None,
    existing_poems: list[dict[str, str]] | None = None,
    fallback_poems: list[dict[str, str]] | None = None,
) -> str:
    return fallback_poem_to_raw(
        select_unused_fallback_poem(
            date=date,
            existing_poems=existing_poems,
            fallback_poems=fallback_poems,
        )
    )


def parse_fallback_refill_response(raw_response: str) -> list[dict[str, str]]:
    response = raw_response.strip()
    if response.startswith("```"):
        response = re.sub(r"^```(?:json)?\s*", "", response, flags=re.IGNORECASE)
        response = re.sub(r"\s*```$", "", response)

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    fallback_poems = [
        fallback_poem
        for value in data
        if (fallback_poem := coerce_fallback_poem(value)) is not None
    ]
    return unique_fallback_poems(fallback_poems)


def build_fallback_refill_prompt(
    existing_poems: list[dict[str, str]],
    fallback_poems: list[dict[str, str]],
    count: int,
) -> str:
    memory = build_poem_memory(existing_poems)
    existing_titles = unique_recent_titles(existing_poems)
    bank_titles = [fallback_poem["title"] for fallback_poem in fallback_poems]
    forbidden_titles = unique_list(existing_titles + bank_titles)

    lines = [
        "Eres el poeta de reserva de luismarrero.me.",
        "",
        f"Genera {count} poemas fallback inéditos en español sobre programación.",
        "",
        "Reglas:",
        "- Responde solo con JSON válido.",
        "- El JSON debe ser un array de objetos con las claves exactas title y poem.",
        "- Cada title debe ser único, concreto y breve.",
        "- Cada poem debe tener entre 4 y 10 versos.",
        "- No uses Markdown, comentarios, introducciones ni texto fuera del JSON.",
        "- Evita repetir imágenes, títulos, versos o estructuras de poemas existentes.",
    ]

    if memory.common_keywords:
        lines.append(
            "- Palabras/imagenes ya muy usadas; evita apoyarte en ellas: "
            + "; ".join(memory.common_keywords)
            + "."
        )

    if forbidden_titles:
        lines.append(
            "- Títulos ya usados o reservados; no los repitas: "
            + "; ".join(forbidden_titles[:200])
            + "."
        )

    if memory.recent_poems:
        lines.append("- Poemas recientes que no debes imitar:")
        for poem in memory.recent_poems:
            opening = str(poem.get("opening") or "")
            lines.append(f"  - {poem['date']}: {poem['title']} | apertura: {opening}")

    lines.extend(
        [
            "",
            "Formato exacto:",
            '[{"title":"Título fresco","poem":"Verso uno\\nVerso dos\\nVerso tres\\nVerso cuatro"}]',
        ]
    )
    return "\n".join(lines)


def unique_list(values: list[str]) -> list[str]:
    unique_values = []
    seen = set()
    for value in values:
        key = normalize_title(value)
        if not key or key in seen:
            continue
        seen.add(key)
        unique_values.append(value)
    return unique_values


def refill_fallback_poem_bank(
    deepseek_api: DeepSeekAPI,
    existing_poems: list[dict[str, str]],
    path: Path = FALLBACK_BANK_PATH,
    threshold: int = FALLBACK_REFILL_THRESHOLD,
    target: int = FALLBACK_REFILL_TARGET,
) -> dict[str, int | bool]:
    fallback_poems = load_fallback_poems(path)
    available_before = len(unused_fallback_poems(fallback_poems, existing_poems))
    stats: dict[str, int | bool] = {
        "available_before": available_before,
        "available_after": available_before,
        "added": 0,
        "refilled": False,
    }

    if available_before >= threshold:
        return stats

    refill_count = max(target - available_before, 0)
    if refill_count == 0:
        return stats

    print(
        "Fallback poem bank is low "
        f"({available_before} unused); requesting {refill_count} new fallbacks."
    )
    response = deepseek_api.call(
        prompt=build_fallback_refill_prompt(
            existing_poems=existing_poems,
            fallback_poems=fallback_poems,
            count=refill_count,
        ),
        temperature=TEMPERATURE,
        max_tokens=FALLBACK_REFILL_MAX_TOKENS,
    )
    if response is None:
        print("Could not refill fallback poem bank; keeping current reserve.")
        return stats

    generated_poems = parse_fallback_refill_response(response.content)
    known_poems = fallback_poems + [
        {"title": poem["title"], "poem": poem["poem"]} for poem in existing_poems
    ]
    new_poems = []
    for generated_poem in generated_poems:
        if is_used_fallback_poem(generated_poem, existing_poems):
            continue
        if is_used_fallback_poem(generated_poem, known_poems):
            continue
        known_poems.append(
            {"title": generated_poem["title"], "poem": generated_poem["poem"]}
        )
        new_poems.append(generated_poem)

    if not new_poems:
        print("DeepSeek returned no usable fallback poems for the reserve.")
        return stats

    fallback_poems.extend(new_poems)
    save_fallback_poems(fallback_poems, path)
    available_after = len(unused_fallback_poems(fallback_poems, existing_poems))
    print(f"Added {len(new_poems)} fallback poems to {path}.")

    stats.update(
        {
            "available_after": available_after,
            "added": len(new_poems),
            "refilled": True,
        }
    )
    return stats


def build_poem_data(
    raw_poem: str | None,
    date: str | None = None,
    existing_poems: list[dict[str, str]] | None = None,
    fallback_poems: list[dict[str, str]] | None = None,
) -> dict[str, str]:
    model = MODEL if raw_poem else "fallback"
    target_date = date or poem_date()
    title, poem = parse_poem(
        raw_poem
        or select_fallback_poem(
            target_date,
            existing_poems=existing_poems,
            fallback_poems=fallback_poems,
        )
    )

    return {
        "model": model,
        "date": target_date,
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
    fallback_poems = load_fallback_poems()
    deepseek_api = DeepSeekAPI(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL)
    generation = generate_poem_with_memory(
        deepseek_api=deepseek_api,
        existing_poems=existing_poems,
        target_date=target_date,
    )
    raw_poem = generation.result.content if generation.result else None
    poem_data = build_poem_data(
        raw_poem,
        date=target_date,
        existing_poems=existing_poems,
        fallback_poems=fallback_poems,
    )
    file_path = save_poem(poem_data)
    print(f"Saved poem to {file_path}")

    fallback_bank_stats = {
        "available_before": len(
            unused_fallback_poems(
                fallback_poems, existing_poems, target_date=target_date
            )
        ),
        "available_after": len(
            unused_fallback_poems(
                fallback_poems, existing_poems, target_date=target_date
            )
        ),
        "added": 0,
        "refilled": False,
    }
    if generation.result is not None:
        poems_after_save = [
            *existing_poems,
            {
                "date": poem_data["date"],
                "title": poem_data["title"],
                "poem": poem_data["poem"],
            },
        ]
        fallback_bank_stats = refill_fallback_poem_bank(
            deepseek_api=deepseek_api,
            existing_poems=poems_after_save,
        )

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
        "fallback_bank": fallback_bank_stats,
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
