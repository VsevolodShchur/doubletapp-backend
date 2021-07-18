#! /bin/sh

python manage.py makemigrations --no-input

python manage.py migrate --no-input

envsubst < ./fixtures/sitesdata.template.json > ./fixtures/sitesdata.json
python manage.py loaddata sitesdata
rm ./fixtures/sitesdata.json

python manage.py collectstatic --no-input

exec gunicorn pets.wsgi:application -b 0.0.0.0:8000 --reload
