#!/bin/sh

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

mysqldump \
  -h db \
  -u root \
  -p"$DB_PASSWORD" \
  "$DB_NAME" \
  > "/backups/imu_assessment_${TIMESTAMP}.sql"

# Remove backups older than 30 days
find /backups -name "imu_assessment_*.sql" -mtime +30 -delete