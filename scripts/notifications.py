from __future__ import annotations

import os
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

CALLMEBOT_PHONE = os.getenv("CALLMEBOT_PHONE")
CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

PRICING_USD_PER_1M = {
    "deepseek-v4-flash": {
        "input_cache_hit": 0.0028,
        "input_cache_miss": 0.14,
        "output": 0.28,
    },
    "deepseek-v4-pro": {
        "input_cache_hit": 0.003625,
        "input_cache_miss": 0.435,
        "output": 0.87,
    },
}
PRICING_MODEL_ALIASES = {
    "deepseek-chat": "deepseek-v4-flash",
    "deepseek-reasoner": "deepseek-v4-flash",
}


def estimate_deepseek_cost_usd(model: str, usage: dict[str, int]) -> float | None:
    pricing_model = PRICING_MODEL_ALIASES.get(model, model)
    pricing = PRICING_USD_PER_1M.get(pricing_model)
    if pricing is None:
        return None

    prompt_tokens = usage.get("prompt_tokens", 0)
    cache_hit_tokens = usage.get("prompt_cache_hit_tokens", 0)
    cache_miss_tokens = usage.get("prompt_cache_miss_tokens")
    if cache_miss_tokens is None:
        cache_miss_tokens = max(prompt_tokens - cache_hit_tokens, 0)

    completion_tokens = usage.get("completion_tokens", 0)
    return (
        (cache_hit_tokens * pricing["input_cache_hit"])
        + (cache_miss_tokens * pricing["input_cache_miss"])
        + (completion_tokens * pricing["output"])
    ) / 1_000_000


def usd_balance_from_response(balance: dict[str, object] | None) -> float | None:
    if not balance:
        return None

    balance_infos = balance.get("balance_infos")
    if not isinstance(balance_infos, list):
        return None

    for info in balance_infos:
        if not isinstance(info, dict):
            continue
        if info.get("currency") != "USD":
            continue

        total_balance = info.get("total_balance")
        if not isinstance(total_balance, str):
            return None

        try:
            return float(total_balance)
        except ValueError:
            return None

    return None


def format_generation_status(generation: Any) -> str:
    if generation.result:
        return "OK"

    if generation.fallback_reason == "repeated_titles":
        return "FALLBACK: DeepSeek repitio titulos y se publico el poema fallback."

    if generation.fallback_reason == "peak_pricing_window":
        return "FALLBACK: ventana pico de DeepSeek; se evito usar el API."

    return "FALLBACK: DeepSeek no genero poema y se publico el poema fallback."


def format_count(value: int) -> str:
    return f"{value:,}"


def format_usd(value: float, decimals: int) -> str:
    return f"USD {value:,.{decimals}f}"


def describe_request_error(error: Exception) -> str:
    response = getattr(error, "response", None)
    status_code = getattr(response, "status_code", None)
    if status_code is not None:
        return f"{error.__class__.__name__} (HTTP {status_code})"

    return error.__class__.__name__


def build_notification_message(
    poem_data: dict[str, str],
    generation: Any,
    balance: dict[str, object] | None,
    model: str | None = None,
) -> str:
    usage = generation.result.usage if generation.result else {}
    pricing_model = model or poem_data.get("model", MODEL)
    estimated_cost = estimate_deepseek_cost_usd(pricing_model, usage) if usage else None
    balance_usd = usd_balance_from_response(balance)

    lines = [
        f"Poema diario {poem_data['date']}",
        f"Generacion: {format_generation_status(generation)}",
        f"Titulo: {poem_data['title']}",
        f"Modelo: {poem_data['model']}",
    ]

    if generation.rejected_titles:
        lines.append("Titulos rechazados: " + "; ".join(generation.rejected_titles))

    if usage:
        total_tokens = usage.get("total_tokens")
        prompt_tokens = usage.get("prompt_tokens")
        cache_hit_tokens = usage.get("prompt_cache_hit_tokens")
        cache_miss_tokens = usage.get("prompt_cache_miss_tokens")
        completion_tokens = usage.get("completion_tokens")
        token_parts = []
        if total_tokens is not None:
            token_parts.append(f"total {format_count(total_tokens)}")
        if prompt_tokens is not None:
            token_parts.append(f"entrada {format_count(prompt_tokens)}")
        if cache_hit_tokens is not None:
            token_parts.append(f"cache hit {format_count(cache_hit_tokens)}")
        if cache_miss_tokens is not None:
            token_parts.append(f"cache miss {format_count(cache_miss_tokens)}")
        if completion_tokens is not None:
            token_parts.append(f"salida {format_count(completion_tokens)}")
        if token_parts:
            lines.append("Tokens: " + ", ".join(token_parts))

    if estimated_cost is not None:
        lines.append(
            f"Costo DeepSeek aprox (este poema): {format_usd(estimated_cost, 8)}"
        )

    if balance_usd is not None:
        lines.append(f"Balance DeepSeek: {format_usd(balance_usd, 2)}")
        if estimated_cost and estimated_cost > 0:
            poems_remaining = int(balance_usd / estimated_cost)
            lines.append(f"Poemas restantes aprox: {format_count(poems_remaining)}")

    return "\n".join(lines)


def send_whatsapp_notification(
    message: str,
    callmebot_phone: str | None = None,
    callmebot_apikey: str | None = None,
) -> bool:
    if callmebot_phone is None:
        callmebot_phone = CALLMEBOT_PHONE
    if callmebot_apikey is None:
        callmebot_apikey = CALLMEBOT_APIKEY

    try:
        import requests
    except ImportError:
        print("requests is not installed; skipping WhatsApp notification.")
        return False

    if callmebot_phone and callmebot_apikey:
        try:
            response = requests.get(
                "https://api.callmebot.com/whatsapp.php",
                params={
                    "phone": callmebot_phone,
                    "text": message,
                    "apikey": callmebot_apikey,
                },
                timeout=30,
            )
            response.raise_for_status()
            print("WhatsApp notification sent via CallMeBot.")
            return True
        except requests.RequestException as error:
            print(
                "Error sending WhatsApp CallMeBot notification: "
                f"{describe_request_error(error)}"
            )
            return False

    print("WhatsApp notification is not configured; skipping.")
    return False


DEEPSEEK_BALANCE_URL = "https://api.deepseek.com/user/balance"


def fetch_deepseek_balance(
    api_key: str | None,
    url: str = DEEPSEEK_BALANCE_URL,
) -> dict[str, object] | None:
    if not api_key:
        return None

    try:
        import requests
    except ImportError:
        return None

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        balance = response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Error fetching DeepSeek balance: {describe_request_error(error)}")
        return None

    return balance if isinstance(balance, dict) else None


def print_cost_summary(
    model: str,
    usage: dict[str, int],
    balance: dict[str, object] | None,
) -> None:
    estimated_cost = estimate_deepseek_cost_usd(model, usage)
    if estimated_cost is None:
        print(f"No pricing data configured for model: {model}")
        return

    print(f"Estimated DeepSeek cost: {format_usd(estimated_cost, 8)}")

    balance_usd = usd_balance_from_response(balance)
    if balance_usd is None:
        return

    print(f"DeepSeek balance: {format_usd(balance_usd, 2)}")
    if estimated_cost > 0:
        poems_remaining = int(balance_usd / estimated_cost)
        print(
            f"Approximate poems remaining at this cost: {format_count(poems_remaining)}"
        )


def print_usage_summary(usage: dict[str, int]) -> None:
    if not usage:
        return

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    cache_hit_tokens = usage.get("prompt_cache_hit_tokens")
    cache_miss_tokens = usage.get("prompt_cache_miss_tokens")

    print("DeepSeek usage:")
    if prompt_tokens is not None:
        print(f"- prompt_tokens: {format_count(prompt_tokens)}")
    if completion_tokens is not None:
        print(f"- completion_tokens: {format_count(completion_tokens)}")
    if total_tokens is not None:
        print(f"- total_tokens: {format_count(total_tokens)}")
    if cache_hit_tokens is not None:
        print(f"- prompt_cache_hit_tokens: {format_count(cache_hit_tokens)}")
    if cache_miss_tokens is not None:
        print(f"- prompt_cache_miss_tokens: {format_count(cache_miss_tokens)}")


def main() -> None:
    import json
    from pathlib import Path

    metadata_path = Path("run_status.json")
    if not metadata_path.exists():
        print(f"No run status file found at {metadata_path}; skipping notification.")
        return

    try:
        with metadata_path.open("r", encoding="utf-8") as f:
            run_data = json.load(f)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error reading run status: {error}")
        return

    # Reconstruct structures for notifications
    class SimpleResult:
        def __init__(self, usage: dict[str, int]):
            self.usage = usage

    class SimpleGeneration:
        def __init__(
            self, result: Any, fallback_reason: str | None, rejected_titles: list[str]
        ):
            self.result = result
            self.fallback_reason = fallback_reason
            self.rejected_titles = rejected_titles

    usage = run_data.get("usage")
    result = SimpleResult(usage=usage) if usage else None
    generation = SimpleGeneration(
        result=result,
        fallback_reason=run_data.get("fallback_reason"),
        rejected_titles=run_data.get("rejected_titles", []),
    )

    poem_data = {
        "date": run_data.get("date"),
        "title": run_data.get("title"),
        "model": run_data.get("model"),
    }

    # Fetch DeepSeek balance
    api_key = os.getenv("DEEPSEEK_API_KEY")
    balance = fetch_deepseek_balance(api_key)

    # Print summaries
    if run_data.get("success") and usage:
        print_usage_summary(usage)
        print_cost_summary(poem_data["model"], usage, balance)

    # Send notification
    notification = build_notification_message(poem_data, generation, balance)
    send_whatsapp_notification(notification)
    print("Notification process finished.")


if __name__ == "__main__":
    main()
