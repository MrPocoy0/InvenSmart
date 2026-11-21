import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from app.services import gemini_service


def test_ask_gemini_valid_response(monkeypatch):
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): return False

    payload = {"candidates": [{"content": {"parts": [{"text": "Prioriza los vencimientos."}]}}]}
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service, "urlopen", lambda *args, **kwargs: Response(json.dumps(payload).encode()))
    assert gemini_service.ask_gemini("¿Qué priorizo?", {}) == "Prioriza los vencimientos."


def test_ask_gemini_requires_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(gemini_service.GeminiServiceError, match="no está configurada"):
        gemini_service.ask_gemini("hola", {})


def test_ask_gemini_invalid_response(monkeypatch):
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self, *args): return False
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service, "urlopen", lambda *args, **kwargs: Response(b"{}"))
    with pytest.raises(gemini_service.GeminiServiceError, match="contenido utilizable"):
        gemini_service.ask_gemini("hola", {})


@pytest.mark.parametrize("status, expected", [
    (400, "Solicitud inválida"),
    (401, "API key"),
    (403, "denegó"),
    (404, "modelo o endpoint"),
    (429, "límite"),
    (500, "error interno"),
])
def test_ask_gemini_http_diagnostics(monkeypatch, status, expected):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    body = json.dumps({"error": {"code": status, "status": "TEST_STATUS", "message": "provider detail test-key"}}).encode()
    error = HTTPError("https://generativelanguage.googleapis.com", status, "error", {}, BytesIO(body))
    monkeypatch.setattr(gemini_service, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(error))
    with pytest.raises(gemini_service.GeminiServiceError) as caught:
        gemini_service.ask_gemini("hola", {})
    assert expected in str(caught.value)
    assert str(status) in str(caught.value)
    assert "test-key" not in str(caught.value)
    assert caught.value.status_code == status
    assert caught.value.provider_code == status
    assert caught.value.provider_status == "TEST_STATUS"


def test_ask_gemini_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError()))
    with pytest.raises(gemini_service.GeminiServiceError, match="conectar"):
        gemini_service.ask_gemini("hola", {})
