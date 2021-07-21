# doubletapp-backend

REST API для ведения учета питомцев (собак и кошек) с возможностью выгрузки списка питомцев через командную строкую.

## API
### 1. POST /pets
### Создать питомца
*request body*

```
{
    "name": "Doge",
    "age": 3,
    "type": "dog"
}
```

<br>

### 2. POST /pets/{id}/photo
### Загрузить фотографию питомца
*from data*

file: binary

<br>

### 3. GET /pets
### Получить список питомцев

*query parameters*

limit: integer (optional, default=20)

offset: integer (optional, default=0)

has_photos: boolean (optional)

&nbsp; has_photos: **true** - возвращаются записи с фотографиями

&nbsp; has_photos: **false** - возвращаются записи без фотографий

&nbsp; has_photos was not provided - возвращаются все записи

<br>

### 4. DELETE /pets
### Удалить питомцев
*request body*
```
{
    "ids": [
        "168bdb84-a647-46f1-979b-6099946f3ed3",
        "32529314-e2ad-4af4-8f4f-1d8e44c09386".
        "a49fa461-858d-4622-8c73-717a25f0ce49"
    ]
}
```

<br>

## Деплой
### Первый запуск
Запустить скрипт `generate_dh_param.sh` для генерации ключа Диффи-Хеллмана.

Из конфигурационного файла Nginx `/nginx/nginx.template.conf` убрать контекст cервера, слушающего 443 порт, чтобы Let's encrypt выполнил ACME-протокол. После получения сертификата перезапустить Nginx с полным конфигурационным файлом.
### Переменные окружения
#### /env/django.env
```
SECRET_KEY - Секретный ключ Django
DEBUG - Режим дебага (False по умолчанию)
ALLOWED_HOSTS - Разрешенные хосты (['*'] по умолчанию )
API_KEY - API ключ
```
#### /env/postgres.env
```
POSTGRES_DB - имя базы данных
POSTGRES_USER - имя пользователя
POSTGRES_PASSWORD - пароль пользователя
```
#### .env - переменные окружения для docker-compose.yml
```
DOMAIN - доменное имя сервера
```
### Запуск
```
docker-compose build
docker-compose up -d
```

<br>

## CLI
Выгрузка питомцев в **stdout** с параметром has_photos: boolean (optional)

```
docker-compose exec web python manage.py export_pets [--has_photos {true,false}]
```