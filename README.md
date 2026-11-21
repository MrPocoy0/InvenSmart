# InvenSmart

InvenSmart es un sistema web académico para la gestión de inventarios y la prevención de pérdidas. Utiliza Python, Flask, SQLAlchemy, MySQL, HTML, CSS y JavaScript.

## Estado actual

### Implementado

- Aplicación Flask con fábrica de aplicación.
- Modelos `Product` y `Category` relacionados.
- Listado, búsqueda, registro, edición y eliminación de productos.
- Registro, edición y eliminación de categorías.
- Validaciones básicas de productos.
- Consulta de productos vencidos y próximos a vencer dentro de 30 días.
- Movimientos de entrada y salida con historial y trazabilidad de stock.
- Alertas de stock bajo, agotado, vencido y próximo a vencer.
- Detección automática de alertas mediante el comando Flask `check-alerts`, sin modificar datos.
- Servicio Docker `scheduler` que ejecuta la detección al iniciar y cada 60 minutos.
- Dashboard con indicadores calculados desde el inventario.
- Asistente consultivo preparado para Google Gemini mediante API.
- Dashboard visual responsive basado en tonos verdes.
- Configuración de MySQL mediante variables de entorno.
- Docker Compose para Flask y MySQL, con volumen persistente y healthcheck.

### Parcial

- La integración con Gemini requiere configurar una clave de Google; sin ella el asistente informa que no está configurado.

### Planificado

- Despliegue real en un entorno externo y ejecución del flujo CI en GitHub.

## Tecnologías

- Python, Flask y Flask-SQLAlchemy / SQLAlchemy.
- MySQL mediante PyMySQL.
- Jinja2, HTML, CSS y JavaScript básico.
- Docker Compose para MySQL.

## Estructura

- `app/models/`: modelos de datos.
- `app/routes/`: rutas Flask.
- `app/services/`: lógica de inventario, alertas, dashboard y asistencia IA.
- `app/static/css/`: estilos.
- `app/templates/`: plantillas HTML/Jinja2.
- `database/`: estructura reservada para datos locales (no versionar).
- `docs/`: documentación técnica, incluyendo el Prompt Engineering de Gemini.
- `tests/`: pruebas automatizadas con SQLite en memoria.
- `docker-compose.yml`: servicios Flask y MySQL.
- `Dockerfile` / `.dockerignore`: imagen de la aplicación y exclusiones de contexto.
- `.github/workflows/ci.yml`: pruebas y Ruff en GitHub Actions.
- `main.py`: punto de entrada de desarrollo local.

## Configuración local preliminar

La configuración actual lee las variables de entorno de `.env`.

1. Copiar `.env.example` como `.env`.
2. Sustituir los valores ficticios por valores locales seguros.
3. Asegurar una instancia MySQL accesible con esos datos.

No se deben versionar `.env`, contraseñas, respaldos SQL ni datos locales.

## Ejecución local de desarrollo

Con las dependencias y la base de datos configuradas:

```powershell
python main.py
```

Este comando inicia Flask en modo de desarrollo local.

### Automatización de alertas

La detección reutiliza el servicio de alertas y realiza una consulta de solo lectura. Puede ejecutarse manualmente o desde una tarea programada externa:

```powershell
flask --app main.py check-alerts
```

El comando informa las cantidades de stock bajo, agotados, vencidos y próximos a vencer. No crea registros, no cambia stock y no registra movimientos. El dashboard y el asistente utilizan el mismo servicio para evitar duplicar lógica.

En Docker, `scheduler` reutiliza la imagen de Flask y ejecuta la misma revisión inmediatamente al iniciar y luego cada 3600 segundos. Solo consulta inventario; si falla una ejecución, registra el error y continúa con el siguiente ciclo. Para iniciarlo sin tocar los demás servicios:

```powershell
docker compose --project-name proyecto_final_inventario_ia up -d scheduler
docker compose --project-name proyecto_final_inventario_ia logs -f scheduler
docker compose --project-name proyecto_final_inventario_ia stop scheduler
```

## Docker

Requisitos: Docker Desktop y un `.env` local con valores válidos. El servicio `mysql` conserva el volumen `mysql_data`; `web` espera el healthcheck de MySQL y usa `MYSQL_HOST=invensmart_mysql` dentro de la red Docker existente.

```powershell
docker compose config
docker compose up --build
```

La aplicación queda publicada en el puerto configurado por Compose. La imagen no ejecuta migraciones automáticamente. Para una base existente, realizar respaldo y revisión antes de aplicar manualmente `flask db upgrade` dentro del contenedor.

## CI/CD

GitHub Actions ejecuta en `main` y en pull requests: instala dependencias, ejecuta las pruebas con SQLite en memoria, valida Ruff y revisa el formato del diff. No utiliza MySQL, secretos de Gemini ni despliegues automáticos.

## Seguridad y recuperación

- Mantener secretos fuera de Git.
- Guardar respaldos fuera de la carpeta del proyecto.
- No ejecutar migraciones sobre una base existente sin respaldo y revisión.
- El punto inicial de recuperación está etiquetado como `etapa1-preparacion-inicial`.
