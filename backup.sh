#!/bin/sh

set -eu

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/imu-assessment_${TIMESTAMP}.sql.gz"

echo "[$(date)] Starting database backup..."

mkdir -p "$BACKUP_DIR"

mysqldump \
  -h "$DB_HOST" \
  -u "$DB_USER" \
  -p"$DB_PASSWORD" \
  "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ ! -s "$BACKUP_FILE" ]; then
    echo "[$(date)] ERROR: Backup file is empty!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "[$(date)] Backup successful: $BACKUP_FILE"

# Delete backups older than 30 days
find "$BACKUP_DIR" \
  -type f \
  -name "imu-assessment_*.sql.gz" \
  -mtime +30 \
  -delete

echo "[$(date)] Old backups cleaned up."

echo "[$(date)] Backup process completed."