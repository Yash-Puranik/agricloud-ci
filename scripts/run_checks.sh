#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${PROJECT_ROOT}/.env"

if ! docker info > /dev/null 2&>1; then
    echo "Docker daemon not found"
    exit 1
fi

HEALTH_CHECK_BACKEND=$(curl -i http://localhost:5000/api/health 2>/dev/null || true)

if [ "$HEALTH_CHECK_BACKEND" -ne 200 ]; then
    echo "Backend service is not healthy. Ensure backend is running"
    exit 1
fi

if command -v openssl >/dev/null 2>&1; then
    GENERATED_PASSWORD=$(openssl rand -hex 24)
else
    GENERATED_PASSWORD=$(tr -dc 'A-Za-z0-9_#$%' < /dev/urandom | head -c 32)
fi

if [ ! -f "$ENV_FILE" ]; then
    echo ".env file not found."
    echo "Creating .env file with default values and generated password."
    cat << EOF > "$ENV_FILE"
POSTGRES_DB=${DEFAULT_DB_NAME}
POSTGRES_USER=${DEFAULT_DB_USER}
POSTGRES_PASSWORD=${GENERATED_PASSWORD}

FLASK_ENV=${DEFAULT_FLASK_ENV}
PORT=${DEFAULT_FLASK_PORT}
METEO_API_URL=${DEFAULT_METEO_URL}
EOF
fi

chmod 600 "${ENV_FILE}"

FIND_DB=$(find . -type f -name "*.db")

if [ -z "$FIND_DB" ]; then
    echo "No .db file found in the project directory."
    exit 1
fi




