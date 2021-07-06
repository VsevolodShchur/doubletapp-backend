#! /bin/sh

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic

exec gunicorn pets.wsgi:application -b 0.0.0.0:8000 --reload
