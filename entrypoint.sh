#!/bin/sh
set -e

echo "=== Iniciando contenedor Autogestión SENA ==="
echo "Target DB: ${DB_HOST}:${DB_PORT:-3306} / Base de datos: ${DB_NAME}"

# Migraciones y siembra de datos de prueba
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "--- Ejecutando makemigrations ---"
  python manage.py makemigrations --noinput || echo "[AVISO] makemigrations finalizado con aviso"
  
  echo "--- Ejecutando migrate ---"
  python manage.py migrate --noinput || echo "[AVISO] migrate finalizado con aviso"
  
  echo "--- Sembrando usuarios demo ---"
  python manage.py seed_demo_users || echo "[AVISO] seed_demo_users finalizado con aviso"
fi

# Recolección de estáticos
if [ "${COLLECT_STATIC:-false}" = "true" ]; then
  echo "--- Recolectando archivos estáticos ---"
  python manage.py collectstatic --noinput || echo "[AVISO] collectstatic finalizado con aviso"
fi

echo "=== Arrancando servidor en puerto ${PORT:-8000} ==="
exec "$@"
