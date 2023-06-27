#!/bin/bash

set -e 
sleep 5
echo "applying migrations"
./manage.py makemigrations users --settings=${DJANGO_SETTINGS_MODULE}
./manage.py makemigrations clients --settings=${DJANGO_SETTINGS_MODULE}
./manage.py migrate --settings=${DJANGO_SETTINGS_MODULE}
echo "finished migrations"
gunicorn --workers=3 --threads=2 --log-level=error --access-logfile /home/desarrollo/logs/access.log  --error-logfile /home/desarrollo/logs/error.log, --log-file /home/desarrollo/logs/gunicorn.log -b 0.0.0.0:8081 init_project.wsgi:application