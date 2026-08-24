#!/bin/sh

set -eu

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/imu-assessment_${TIMESTAMP}.sql.gz"
TEMP_FILE="${BACKUP_FILE}.tmp"

echo "[$(date)] Starting database backup..."

mkdir -p "$BACKUP_DIR"

if mysqldump \
  -h "$DB_HOST" \
  -u "$DB_USER" \
  -p"$DB_PASSWORD" \
  "$DB_NAME" | gzip > "$TEMP_FILE"
then
    :
else
    echo "[$(date)] ERROR: mysqldump failed!"
    rm -f "$TEMP_FILE"
    exit 1
fi

if ! gzip -t "$TEMP_FILE"; then
    echo "[$(date)] ERROR: Backup gzip file is corrupt!"
    rm -f "$TEMP_FILE"
    exit 1
fi

if [ "$(gzip -l "$TEMP_FILE" | awk 'NR==2 {print $2}')" -eq 0 ]; then
    echo "[$(date)] ERROR: Backup contains no SQL data!"
    rm -f "$TEMP_FILE"
    exit 1
fi

mv "$TEMP_FILE" "$BACKUP_FILE"

echo "[$(date)] Backup successful: $BACKUP_FILE"

# Delete backups older than 30 days
find "$BACKUP_DIR" \
  -type f \
  -name "imu-assessment_*.sql.gz" \
  -mtime +30 \
  -delete

echo "[$(date)] Old backups cleaned up."
echo "[$(date)] Backup process completed."