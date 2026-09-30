# 🚀 Backend Web API - Autogestión SENA

API RESTful y WebSocket de alto rendimiento para el sistema de **Autogestión SENA**, desarrollada con **Django 5**, **Django REST Framework (DRF)**, **Channels / Daphne** y **Celery**.

---

## 🌐 Despliegues y Entornos Activos

| Servicio | Proveedor | URL / Endpoint | Estado |
| :--- | :--- | :--- | :--- |
| **API REST en Producción** | Render (Docker Web Service) | [https://autogestion-sena-api.onrender.com](https://autogestion-sena-api.onrender.com) | `Online` 🟢 |
| **Documentación Swagger / OpenAPI** | drf-yasg | [https://autogestion-sena-api.onrender.com/swagger/](https://autogestion-sena-api.onrender.com/swagger/) | `Online` 🟢 |
| **Documentación ReDoc** | drf-yasg | [https://autogestion-sena-api.onrender.com/redoc/](https://autogestion-sena-api.onrender.com/redoc/) | `Online` 🟢 |
| **Base de Datos Cloud** | Aiven Cloud MySQL 8.4 | Host: `mysql-25dc6630-accesorioslilis2026.b.aivencloud.com:28668` | `Online` 🟢 |

---

## 🔑 Credenciales de Prueba y Demostración (Demo Accounts)

Para evaluación y pruebas en vivo, todos los roles cuentan con contraseña unificada y código de 2FA predeterminado:

- **Contraseña Común:** `Sena2026*`
- **Código de Verificación 2FA:** `123456`

| Rol | Correo Electrónico | Alcance de Permisos |
| :--- | :--- | :--- |
| **Administrador** | `admin.demo@sena.edu.co` | Control total, gestión de usuarios, roles, módulos y auditoría |
| **Aprendiz** | `aprendiz.demo@soy.sena.edu.co` | Consulta de fichas, estado de etapa productiva y solicitudes |
| **Instructor** | `instructor.demo@sena.edu.co` | Asignación y seguimiento de aprendices, reportes y bitácoras |
| **Coordinador** | `coordinador.demo@sena.edu.co` | Aprobación de cartas, balanceo de instructores y reportes ejecutivos |
| **Operador Sofia Plus** | `sofia.demo@sena.edu.co` | Sincronización de datos con Sofia Plus y carga masiva Excel |

---

## 🏗️ Arquitectura Técnica

- **Framework:** Python 3.12+ / Django 5.0.7
- **Arquitectura de Software:** DDD simplificado con capas desacopladas:
  - `entity/`: Modelos ORM de dominio.
  - `repositories/`: Capa de persistencia y consultas tipadas.
  - `services/`: Lógica de negocio pura y orquestación.
  - `views/`: ViewSets DRF con serializadores y validación.
- **Base de Datos:** MySQL 8.4 (Soporte nativo para variables individuales o URI `DATABASE_URL` con SSL).
- **Asincronía y Tareas:** Celery con broker Redis y Celery Beat para tareas programadas (ej. desactivación de instructores vencidos).
- **WebSockets:** Django Channels / Daphne con enrutamiento asíncrono para notificaciones en tiempo real.

---

## ⚙️ Configuración y Variables de Entorno

Crea un archivo `.env` en la raíz de `backend/` basado en la siguiente plantilla:

```ini
# Django Core
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,autogestion-sena-api.onrender.com

# Base de Datos (Opcional formato URI unificado)
DATABASE_URL=mysql://avnadmin:PASSWORD@mysql-25dc6630-accesorioslilis2026.b.aivencloud.com:28668/bdautogestion?ssl-mode=REQUIRED

# Base de Datos (Formato individual alternativo)
DB_NAME=bdautogestion
DB_USER=avnadmin
DB_PASSWORD=tu-password-aiven
DB_HOST=mysql-25dc6630-accesorioslilis2026.b.aivencloud.com
DB_PORT=28668
DB_SSL=true

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Correo (Para 2FA y Notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@sena.edu.co
EMAIL_HOST_PASSWORD=tu-app-password
EMAIL_USE_TLS=True
```

---

## 💻 Instalación y Ejecución Local

### Opción 1: Entorno Virtual Python

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate      # En Windows
# source venv/bin/activate   # En Linux/macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar migraciones
python manage.py migrate

# 4. (Opcional) Cargar datos de prueba
python manage.py seed_demo_users

# 5. Iniciar servidor ASGI con Daphne
daphne -b 127.0.0.1 -p 8000 core.asgi:application
```

### Opción 2: Docker Compose

```bash
# Construir y levantar todos los contenedores (API, Redis, Celery Worker, Celery Beat)
docker-compose up --build -d

# Ver logs en vivo
docker-compose logs -f
```

---

## 🧪 Pruebas Automatizadas

El proyecto incluye suites de pruebas unitarias y de integración para los dominios de seguridad y general:

```bash
# Ejecutar suite de pruebas de seguridad
python manage.py test apps.security.test

# Ejecutar suite de pruebas generales
python manage.py test apps.general.test
```

---

## 🛡️ Políticas de Git y Ramas

El repositorio sigue un estricto flujo de tres ramas:
1. `dev`: Desarrollo activo e integración continua.
2. `QA`: Pruebas de aseguramiento de calidad y staging.
3. `main`: Producción estable y despliegues oficiales en Render.