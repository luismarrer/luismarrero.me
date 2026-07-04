import json
import re
from datetime import datetime, timezone

import requests

import scripts.deepseek_monitor as deepseek_monitor
import scripts.generate_poem as generate_poem
import scripts.notifications as notifications


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


def test_parse_poem_strips_markdown_title_markup():
    title, body = generate_poem.parse_poem("### **Titulo generado**\n\nLinea uno")

    assert title == "Titulo generado"
    assert body == "Linea uno"


def test_build_poem_data_uses_fallback_when_api_fails():
    poem_data = generate_poem.build_poem_data(None)

    assert poem_data["model"] == "fallback"
    assert poem_data["title"] == "Bitácora del Código"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", poem_data["date"])
    assert "La pantalla respira" in poem_data["poem"]


def test_build_poem_data_uses_configured_model_for_api_response(monkeypatch):
    monkeypatch.setattr(generate_poem, "MODEL", "deepseek-test")

    poem_data = generate_poem.build_poem_data(
        "Titulo\n\nLinea uno\nLinea dos",
        date="2026-01-02",
    )

    assert poem_data == {
        "model": "deepseek-test",
        "date": "2026-01-02",
        "title": "Titulo",
        "poem": "Linea uno\nLinea dos",
    }


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


def test_deepseek_api_sends_expected_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["raised_for_status"] = True

        def json(self):
            return {
                "choices": [{"message": {"content": "Titulo\n\nLinea"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                    "ignored": "not-int",
                },
            }

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    api = generate_poem.DeepSeekAPI(
        api_key="secret",
        url="https://example.com/chat",
        model="deepseek-test",
    )

    result = api.call(prompt="Escribe", temperature=0.4, max_tokens=123)

    assert result == generate_poem.DeepSeekResult(
        content="Titulo\n\nLinea",
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    )
    assert captured == {
        "url": "https://example.com/chat",
        "json": {
            "model": "deepseek-test",
            "messages": [{"role": "user", "content": "Escribe"}],
            "temperature": 0.4,
            "max_tokens": 123,
            "thinking": generate_poem.NON_THINKING_CONFIG,
        },
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret",
        },
        "timeout": 120,
        "raised_for_status": True,
    }


def test_deepseek_peak_pricing_windows_use_beijing_time():
    assert generate_poem.is_deepseek_peak_pricing_time(
        datetime(2026, 7, 4, 1, 0, tzinfo=timezone.utc)
    )
    assert not generate_poem.is_deepseek_peak_pricing_time(
        datetime(2026, 7, 4, 4, 0, tzinfo=timezone.utc)
    )
    assert generate_poem.is_deepseek_peak_pricing_time(
        datetime(2026, 7, 4, 6, 0, tzinfo=timezone.utc)
    )
    assert not generate_poem.is_deepseek_peak_pricing_time(
        datetime(2026, 7, 4, 10, 0, tzinfo=timezone.utc)
    )


def test_generate_poem_with_memory_skips_api_during_peak_pricing(monkeypatch):
    monkeypatch.setattr(generate_poem, "should_skip_deepseek_for_peak_pricing", lambda: True)

    class FakeAPI:
        def call(self, prompt, temperature, max_tokens):
            raise AssertionError("DeepSeek should not be called during peak pricing")

    generation = generate_poem.generate_poem_with_memory(
        deepseek_api=FakeAPI(),
        existing_poems=[],
        target_date="2026-01-02",
    )

    assert generation == generate_poem.PoemGeneration(
        result=None,
        fallback_reason="peak_pricing_window",
        rejected_titles=[],
    )


def test_build_poem_prompt_uses_recent_memory_and_rejected_titles():
    prompt = generate_poem.build_poem_prompt(
        existing_poems=[
            {
                "date": "2026-01-01",
                "title": "Algoritmo Poético",
                "poem": "Linea",
            },
            {
                "date": "2026-01-02",
                "title": "Algoritmo Poético",
                "poem": "Linea",
            },
        ],
        target_date="2026-01-03",
        attempt=2,
        rejected_titles=["Algoritmo Poético"],
    )

    assert "Poemas recientes" in prompt
    assert "apertura: Linea" in prompt
    assert "keywords:" in prompt
    assert "Títulos frecuentes prohibidos: Algoritmo Poético." in prompt
    assert "Títulos rechazados en intentos anteriores: Algoritmo Poético." in prompt


def test_build_poem_prompt_has_strict_mode_for_repeated_titles():
    prompt = generate_poem.build_poem_prompt(
        existing_poems=[
            {
                "date": "2026-01-01",
                "title": "Algoritmo Poético",
                "poem": "Linea",
            }
        ],
        target_date="2026-01-02",
        force_distinct_title=True,
    )

    assert "Modo anti-repetición estricto" in prompt
    assert "No uses exactamente ninguno de estos títulos ya existentes" in prompt
    assert "Algoritmo Poético" in prompt


def test_generate_poem_with_memory_retries_repeated_title_then_succeeds(monkeypatch):
    monkeypatch.setattr(generate_poem, "MAX_ATTEMPTS", 3)
    existing_poems = [
        {"date": "2026-01-01", "title": "Algoritmo Poético", "poem": "Linea"}
    ]

    class FakeAPI:
        def __init__(self):
            self.prompts = []
            self.responses = [
                generate_poem.DeepSeekResult(
                    content="Algoritmo Poético\n\nLinea repetida",
                    usage={},
                ),
                generate_poem.DeepSeekResult(
                    content="Circuito Nuevo\n\nLinea fresca",
                    usage={"total_tokens": 20},
                ),
            ]

        def call(self, prompt, temperature, max_tokens):
            self.prompts.append(prompt)
            return self.responses.pop(0)

    api = FakeAPI()

    generation = generate_poem.generate_poem_with_memory(
        deepseek_api=api,
        existing_poems=existing_poems,
        target_date="2026-01-02",
    )

    assert generation == generate_poem.PoemGeneration(
        result=generate_poem.DeepSeekResult(
            content="Circuito Nuevo\n\nLinea fresca",
            usage={"total_tokens": 20},
        ),
        fallback_reason=None,
        rejected_titles=["Algoritmo Poético"],
    )
    assert len(api.prompts) == 2
    assert (
        "Títulos rechazados en intentos anteriores: Algoritmo Poético."
        in (api.prompts[1])
    )


def test_generate_poem_with_memory_uses_strict_retry_before_fallback(monkeypatch):
    monkeypatch.setattr(generate_poem, "MAX_ATTEMPTS", 1)
    existing_poems = [
        {"date": "2026-01-01", "title": "Algoritmo Poético", "poem": "Linea"}
    ]

    class FakeAPI:
        def __init__(self):
            self.prompts = []
            self.responses = [
                generate_poem.DeepSeekResult(
                    content="Algoritmo Poético\n\nLinea repetida",
                    usage={},
                ),
                generate_poem.DeepSeekResult(
                    content="Algoritmo Poético\n\nOtra linea repetida",
                    usage={},
                ),
            ]

        def call(self, prompt, temperature, max_tokens):
            self.prompts.append(prompt)
            return self.responses.pop(0)

    api = FakeAPI()

    generation = generate_poem.generate_poem_with_memory(
        deepseek_api=api,
        existing_poems=existing_poems,
        target_date="2026-01-02",
    )

    assert generation == generate_poem.PoemGeneration(
        result=None,
        fallback_reason="repeated_titles",
        rejected_titles=["Algoritmo Poético", "Algoritmo Poético"],
    )
    assert len(api.prompts) == 2
    assert "Modo anti-repetición estricto" in api.prompts[1]


def test_generate_poem_with_memory_reports_deepseek_unavailable():
    class FakeAPI:
        def call(self, prompt, temperature, max_tokens):
            return None

    generation = generate_poem.generate_poem_with_memory(
        deepseek_api=FakeAPI(),
        existing_poems=[],
        target_date="2026-01-02",
    )

    assert generation == generate_poem.PoemGeneration(
        result=None,
        fallback_reason="deepseek_unavailable",
        rejected_titles=[],
    )


def test_build_notification_message_reports_success_and_cost():
    message = notifications.build_notification_message(
        poem_data={
            "model": "deepseek-v4-flash",
            "date": "2026-01-02",
            "title": "Circuito Nuevo",
            "poem": "Linea fresca",
        },
        generation=generate_poem.PoemGeneration(
            result=generate_poem.DeepSeekResult(
                content="Circuito Nuevo\n\nLinea fresca",
                usage={
                    "prompt_tokens": 2020,
                    "total_tokens": 2070,
                    "prompt_cache_hit_tokens": 410,
                    "prompt_cache_miss_tokens": 1590,
                    "completion_tokens": 50,
                },
            ),
            fallback_reason=None,
            rejected_titles=["Algoritmo Poético"],
        ),
        balance={
            "balance_infos": [
                {"currency": "USD", "total_balance": "10.00"},
            ]
        },
    )

    assert "Generacion: OK" in message
    assert "Titulos rechazados: Algoritmo Poético" in message
    assert "Tokens: total 2,070, entrada 2,020" in message
    assert "cache hit 410, cache miss 1,590, salida 50" in message
    assert "Costo DeepSeek aprox (este poema): USD 0.00023775" in message
    assert "Balance DeepSeek: USD 10.00" in message
    assert "Poemas restantes aprox: 42,061" in message
    assert "$" not in message


def test_build_notification_message_reports_fallback():
    message = notifications.build_notification_message(
        poem_data={
            "model": "fallback",
            "date": "2026-01-02",
            "title": "Bitácora del Código",
            "poem": "Linea",
        },
        generation=generate_poem.PoemGeneration(
            result=None,
            fallback_reason="deepseek_unavailable",
            rejected_titles=[],
        ),
        balance=None,
    )

    assert "FALLBACK: DeepSeek no genero poema" in message


def test_build_notification_message_reports_peak_pricing_fallback():
    message = notifications.build_notification_message(
        poem_data={
            "model": "fallback",
            "date": "2026-01-02",
            "title": "Bitácora del Código",
            "poem": "Linea",
        },
        generation=generate_poem.PoemGeneration(
            result=None,
            fallback_reason="peak_pricing_window",
            rejected_titles=[],
        ),
        balance=None,
    )

    assert "FALLBACK: ventana pico de DeepSeek" in message


def test_build_notification_message_uses_saved_poem_model_for_cost():
    message = notifications.build_notification_message(
        poem_data={
            "model": "deepseek-v4-pro",
            "date": "2026-01-02",
            "title": "Circuito Nuevo",
        },
        generation=generate_poem.PoemGeneration(
            result=generate_poem.DeepSeekResult(
                content="Circuito Nuevo\n\nLinea fresca",
                usage={
                    "prompt_tokens": 1_000_000,
                    "prompt_cache_hit_tokens": 0,
                    "prompt_cache_miss_tokens": 1_000_000,
                    "completion_tokens": 0,
                },
            ),
            fallback_reason=None,
            rejected_titles=[],
        ),
        balance=None,
    )

    assert "Costo DeepSeek aprox (este poema): USD 0.43500000" in message


def test_send_whatsapp_notification_uses_callmebot(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["raised_for_status"] = True

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    sent = notifications.send_whatsapp_notification(
        "hello\nworld",
        callmebot_phone="+17875551234",
        callmebot_apikey="callmebot-secret",
    )

    assert sent is True
    assert captured == {
        "url": "https://api.callmebot.com/whatsapp.php",
        "params": {
            "phone": "+17875551234",
            "text": "hello\nworld",
            "apikey": "callmebot-secret",
        },
        "timeout": 30,
        "raised_for_status": True,
    }


def test_send_whatsapp_notification_redacts_callmebot_error(monkeypatch, capsys):
    class FakeResponse:
        status_code = 403

        def raise_for_status(self):
            raise requests.HTTPError(
                "403 Client Error for url: "
                "https://api.callmebot.com/whatsapp.php?"
                "phone=15551234567&text=hello&apikey=secret-key",
                response=self,
            )

    def fake_get(url, params, timeout):
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    sent = notifications.send_whatsapp_notification(
        "hello",
        callmebot_phone="15551234567",
        callmebot_apikey="secret-key",
    )

    output = capsys.readouterr().out
    assert sent is False
    assert "HTTPError (HTTP 403)" in output
    assert "secret-key" not in output
    assert "15551234567" not in output


def test_estimate_deepseek_cost_uses_cache_hit_and_miss_tokens():
    cost = notifications.estimate_deepseek_cost_usd(
        "deepseek-v4-flash",
        {
            "prompt_tokens": 120,
            "prompt_cache_hit_tokens": 100,
            "prompt_cache_miss_tokens": 20,
            "completion_tokens": 50,
        },
    )

    assert cost == (100 * 0.0028 + 20 * 0.14 + 50 * 0.28) / 1_000_000


def test_usd_balance_from_response_reads_usd_total():
    balance = notifications.usd_balance_from_response(
        {
            "is_available": True,
            "balance_infos": [
                {"currency": "CNY", "total_balance": "100.00"},
                {"currency": "USD", "total_balance": "12.34"},
            ],
        }
    )

    assert balance == 12.34


def test_fetch_deepseek_balance_sends_authorization_header(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            captured["raised_for_status"] = True

        def json(self):
            return {"is_available": True, "balance_infos": []}

    def fake_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    balance = notifications.fetch_deepseek_balance(
        api_key="secret",
        url="https://example.com/balance",
    )

    assert balance == {"is_available": True, "balance_infos": []}
    assert captured == {
        "url": "https://example.com/balance",
        "headers": {"Authorization": "Bearer secret"},
        "timeout": 30,
        "raised_for_status": True,
    }


def test_parse_deepseek_monitor_targets_from_env():
    targets = deepseek_monitor.parse_targets(
        "pricing=https://example.com/pricing, x=https://example.com/x"
    )

    assert targets == [
        deepseek_monitor.MonitorTarget("pricing", "https://example.com/pricing"),
        deepseek_monitor.MonitorTarget("x", "https://example.com/x"),
    ]


def test_deepseek_monitor_detects_changed_target(monkeypatch):
    results = iter(
        [
            deepseek_monitor.FetchResult(
                status_code=200,
                content_hash="new-hash",
                content_length=10,
            )
        ]
    )

    def fake_fetch(target):
        return next(results)

    monkeypatch.setattr(deepseek_monitor, "fetch_target", fake_fetch)

    state, changes, errors = deepseek_monitor.monitor_targets(
        [deepseek_monitor.MonitorTarget("pricing", "https://example.com/pricing")],
        {
            "targets": {
                "pricing": {
                    "url": "https://example.com/pricing",
                    "content_hash": "old-hash",
                    "last_changed_at": "2026-01-01T00:00:00+00:00",
                }
            }
        },
        checked_at="2026-01-02T00:00:00+00:00",
    )

    assert changes == ["pricing: https://example.com/pricing"]
    assert errors == []
    assert state["targets"]["pricing"]["content_hash"] == "new-hash"
    assert state["targets"]["pricing"]["last_changed_at"] == "2026-01-02T00:00:00+00:00"


def test_deepseek_monitor_initializes_without_alert(monkeypatch):
    def fake_fetch(target):
        return deepseek_monitor.FetchResult(
            status_code=200,
            content_hash="first-hash",
            content_length=10,
        )

    monkeypatch.setattr(deepseek_monitor, "fetch_target", fake_fetch)

    state, changes, errors = deepseek_monitor.monitor_targets(
        [deepseek_monitor.MonitorTarget("pricing", "https://example.com/pricing")],
        {},
        checked_at="2026-01-02T00:00:00+00:00",
    )

    assert changes == []
    assert errors == []
    assert state["targets"]["pricing"]["content_hash"] == "first-hash"
