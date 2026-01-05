#!/bin/bash

echo "======================================"
echo "Running Database Migrations"
echo "======================================"

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=fintrack_pass psql -h postgres -U fintrack_user -d fintrack -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
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
