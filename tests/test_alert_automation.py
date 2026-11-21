def test_alert_detection_command_is_read_only(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["check-alerts"])
    assert result.exit_code == 0
    assert "Alertas detectadas" in result.output


def test_dashboard_uses_automatic_alert_detection(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Alertas de inventario" in response.get_data(as_text=True)
