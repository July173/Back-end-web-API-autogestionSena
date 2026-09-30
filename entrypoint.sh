#!/bin/sh
set -e

DB_PASS_VAL="${DB_PASSWORD:-$DB_PASS}"

echo "Waiting for database at ${DB_HOST}:${DB_PORT:-3306}..."

# If DB host and user are provided, wait until MySQL is reachable
if [ -n "$DB_HOST" ] && [ -n "$DB_USER" ]; then
  MAX_TRIES=15
  COUNT=0
  until mysqladmin ping -h "$DB_HOST" -P "${DB_PORT:-3306}" -u"$DB_USER" -p"$DB_PASS_VAL" >/dev/null 2>&1 || [ $COUNT -ge $MAX_TRIES ]; do
    echo "Waiting for MySQL at $DB_HOST:${DB_PORT:-3306}... ($COUNT/$MAX_TRIES)"
    sleep 2
    COUNT=$((COUNT + 1))
  done
fi

echo "Database ready or check completed — checking migrations"
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "RUN_MIGRATIONS=true — applying migrations"
  python manage.py makemigrations --noinput || true
  python manage.py migrate --noinput
  python manage.py seed_demo_users || true
else
  echo "RUN_MIGRATIONS not true — skipping migrations"
fi

if [ "${COLLECT_STATIC:-false}" = "true" ]; then
  echo "COLLECT_STATIC=true — collecting static files"
  python manage.py collectstatic --noinput || true
fi

echo "Starting process: $@"
exec "$@"
