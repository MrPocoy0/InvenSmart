import pytest


NAV_LABELS = ["Dashboard", "Productos", "Movimientos", "Vencimientos", "Categorías", "Alertas", "Reportes", "Asistente IA"]
ROUTES = ["/", "/productos/", "/movimientos/", "/vencimientos/", "/categorias/", "/alertas/", "/reportes/", "/asistente/"]


@pytest.mark.parametrize("path", ROUTES)
def test_all_modules_render_complete_navigation(client, path):
    response = client.get(path)
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    for label in NAV_LABELS:
        assert label in body


def test_navigation_endpoints_are_reachable(client):
    response = client.get("/alertas/")
    body = response.get_data(as_text=True)
    assert "/asistente/" in body
    assert "/reportes/" in body
    assert "/" in body


def test_direct_navigation_matrix(client):
    pairs = {
        "/categorias/": "/asistente/",
        "/vencimientos/": "/asistente/",
        "/alertas/": "/asistente/",
        "/movimientos/": "/reportes/",
        "/reportes/": "/alertas/",
        "/asistente/": "/productos/",
        "/productos/": "/categorias/",
    }
    for source, target in pairs.items():
        body = client.get(source).get_data(as_text=True)
        assert target in body
