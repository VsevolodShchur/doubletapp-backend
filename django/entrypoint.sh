#! /bin/sh

python manage.py makemigrations --no-input

python manage.py migrate --no-input

cd ./pets/fixtures/
envsubst < sitesdata.template.json > sitesdata.json
cd ../..
python manage.py loaddata sitesdata
rm ./pets/fixtures/sitesdata.json

python manage.py collectstatic --no-input

exec gunicorn pets.wsgi:application -b 0.0.0.0:8000 --reload
