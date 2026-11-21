import re


def _csrf_token(client):
    response = client.get("/categorias/")
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match
    return match.group(1)


def test_post_without_csrf_token_is_rejected(csrf_app):
    response = csrf_app.test_client().post(
        "/categorias/crear", data={"name": "Sin token"}
    )
    assert response.status_code == 400


def test_post_with_valid_csrf_token_is_accepted(csrf_app):
    client = csrf_app.test_client()
    response = client.post(
        "/categorias/crear",
        data={"name": "Con token", "csrf_token": _csrf_token(client)},
    )
    assert response.status_code == 302


def test_post_with_invalid_csrf_token_is_rejected(csrf_app):
    response = csrf_app.test_client().post(
        "/categorias/crear",
        data={"name": "Token inválido", "csrf_token": "invalid-token"},
    )
    assert response.status_code == 400
