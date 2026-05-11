#!/bin/bash
set -e

graceful_shutdown() {
  echo "Shutting down..."
  exit 0
}
trap graceful_shutdown SIGTERM SIGINT

echo "Waiting for database proxy (PgBouncer)..."
until pg_isready -h pgbouncer -p 6432 -U "${POSTGRES_USERNAME}"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Applying database migrations..."
for i in {1..5}; do
  if alembic upgrade head; then
    echo "Migrations applied successfully."
    break
  else
    echo "Migration failed, retrying in $i seconds..."
    sleep $i
  fi
  if [ $i -eq 5 ]; then
    echo "Could not apply migrations. Exiting."
    exit 1
  fi
done

echo "Starting application..."
exec "$@"
