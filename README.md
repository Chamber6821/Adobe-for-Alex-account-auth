# Account Auth

Сервис для автоматической регистрации и авторизации пользователей на сайте Adobe

# Установка и запуск

```bash
git clone https://github.com/snrteftelya/account-auth
cd account-auth
cp .env.template .env
```

## Запуск для разработки:
```bash
chmod +x auth-service.sh
./auth-service.sh dev      
```

## Запуск для деплоя:
```bash
chmod +x auth-service.sh
./auth-service.sh deploy      
```

# REST API

## `POST /register`

Зарегистрировать пользователя в системе.

### Request Body:
```json
{
  "email": "user-email",
  "password": "user-password"
}
```

### Response:
```json
{
  "token": "example-token-123"
}
```

## `POST /login`

Вход пользователя в систему.

### Request Body:
```json
{
  "email": "user-email",
  "password": "user-password"
}
```

### Response:
```json
{
  "token": "example-token-123"
}
```

# Как внести свои изменения?

- Форкаешь репозиторий
- Клонишь свой форк
- Создаешь отдельную ветку для своиз изменений
(это важно для избежания гемороя при параллельной разработке нескольких фич)
- Комитишь изменения в свою ветку
- Оформляешь Pull Request
- Если твои изменения исправляют какие-то проблемы из раздела Issue,
то добавь их номера в описании PR в следующем виде:
```
Fixes #1
Fixes #2
Fixes #3
```
[Почему так стоит делать](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)