#!/bin/bash
# Must set:
# SQL_HOST, SQL_USER, SQL_PASS, SQL_DB, GCP_GS_BUCKET
gcloud auth activate-service-account --key-file /etc/gcp-sa/service-account.json

# download target file
gsutil cp gs://${GCP_GS_BUCKET}/${BACKUP_FILE_NAME} .

# drop old db, apply backup
mysql --user=$SQL_USER --password=$SQL_PASS -h $SQL_HOST $SQL_DB -e "drop database $SQL_DB;"
mysql --user=$SQL_USER --password=$SQL_PASS -h $SQL_HOST -e "create database $SQL_DB;"
mysql -h $SQL_HOST --user=$SQL_USER --password=$SQL_PASS $SQL_DB < $BACKUP_FILE_NAME