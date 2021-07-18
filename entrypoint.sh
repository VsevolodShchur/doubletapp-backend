#! /bin/sh

python manage.py makemigrations --no-input

python manage.py migrate --no-input

envsubst < sitesdata.template.json > sitesdata.json
python manage.py loaddata sites sitesdata.json

if [ "$DEBUG" = "TRUE" ]; then
    python manage.py collectstatic --no-input
fi

exec gunicorn pets.wsgi:application -b 0.0.0.0:8000 --reload
