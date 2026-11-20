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
- Dashboard visual responsive basado en tonos verdes.
- Configuración de MySQL mediante variables de entorno.
- Docker Compose para el servicio MySQL.

### Parcial

- El dashboard usa indicadores y alertas de demostración, no métricas calculadas del inventario real.
- Docker Compose configura MySQL, pero no contiene un servicio Flask ni es un despliegue completo de la aplicación web.
- `database/`, `docs/` y `tests/` existen, pero están vacíos.
- `app/services/` existe como estructura inicial, sin servicios de negocio implementados.

### Planificado

- Movimientos de inventario e historial.
- Alertas automáticas e indicadores basados en datos reales.
- Integración de IA para recomendaciones justificadas.
- Migraciones, pruebas automatizadas, Docker para Flask y CI/CD.

## Tecnologías

- Python, Flask y Flask-SQLAlchemy / SQLAlchemy.
- MySQL mediante PyMySQL.
- Jinja2, HTML, CSS y JavaScript básico.
- Docker Compose para MySQL.

## Estructura

- `app/models/`: modelos de datos.
- `app/routes/`: rutas Flask.
- `app/services/`: estructura reservada para servicios.
- `app/static/css/`: estilos.
- `app/templates/`: plantillas HTML/Jinja2.
- `database/`, `docs/` y `tests/`: estructuras reservadas actualmente vacías.
- `docker-compose.yml`: configuración actual de MySQL.
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

## Docker

`docker-compose.yml` configura actualmente MySQL 8.4 con volumen persistente y healthcheck. No configura todavía un servicio Flask.

## Seguridad y recuperación

- Mantener secretos fuera de Git.
- Guardar respaldos fuera de la carpeta del proyecto.
- No ejecutar migraciones sobre una base existente sin respaldo y revisión.
- El punto inicial de recuperación está etiquetado como `etapa1-preparacion-inicial`.
