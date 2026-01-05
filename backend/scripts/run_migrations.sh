#!/bin/bash

echo "======================================"
echo "Running Database Migrations"
echo "======================================"

echo "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

until PGPASSWORD=fintrack_pass psql -h postgres -U fintrack_user -d fintrack -c '\q' 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "PostgreSQL did not become ready in time. Exiting..."
    exit 1
  fi
  echo "PostgreSQL is unavailable - sleeping (попытка $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done

echo "PostgreSQL is ready!"

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "======================================"
    echo "✓ Migrations completed successfully!"
    echo "======================================"
else
    echo "======================================"
    echo "✗ Migration failed!"
    echo "======================================"
    exit 1
fi
