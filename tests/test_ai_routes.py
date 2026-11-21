def test_ai_get(client):
    response = client.get("/asistente/")
    assert response.status_code == 200
    assert "Asistente IA" in response.get_data(as_text=True)


def test_ai_empty_question(client):
    response = client.post("/asistente/", data={"question": ""})
    assert response.status_code == 200
    assert "Escribe una pregunta" in response.get_data(as_text=True)


def test_ai_long_question(client):
    response = client.post("/asistente/", data={"question": "x" * 1001})
    assert response.status_code == 200
    assert "1000 caracteres" in response.get_data(as_text=True)


def test_ai_csrf_rejects_post(csrf_app):
    response = csrf_app.test_client().post("/asistente/", data={"question": "hola"})
    assert response.status_code == 400


def test_ai_post_uses_provider(client, monkeypatch):
    from app.routes import ai_routes

    monkeypatch.setattr(ai_routes, "ask_gemini", lambda question, context: "Respuesta de prueba")
    response = client.post("/asistente/", data={"question": "¿Qué priorizo?"})
    assert response.status_code == 200
    assert "Respuesta de prueba" in response.get_data(as_text=True)


def test_ai_provider_error_is_controlled(client, monkeypatch):
    from app.routes import ai_routes
    from app.services.gemini_service import GeminiServiceError

    def fail(*args, **kwargs):
        raise GeminiServiceError("Proveedor no disponible")

    monkeypatch.setattr(ai_routes, "ask_gemini", fail)
    response = client.post("/asistente/", data={"question": "hola"})
    assert response.status_code == 200
    assert "Proveedor no disponible" in response.get_data(as_text=True)
