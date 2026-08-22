# GD-Store — скелет проекта (Steam-like магазин игр)

Стек: **React (Vite) + Django REST Framework + MSSQL**, команда 4 человека (3 бекенда + 1 фронтенд).

## Структура репозитория

```
gd-store/
├── backend/                  # Django REST API
│   ├── config/                # settings.py, urls.py, wsgi/asgi
│   ├── apps/
│   │   ├── accounts/           # Dev 1 — юзеры, JWT-авторизация, профили, друзья
│   │   ├── catalog/             # Dev 2 — игры, жанры, теги, скриншоты, поиск/фильтры
│   │   ├── store/                # Dev 3 — корзина, вишлист, заказы
│   │   ├── payments/             # Dev 3 — платежи, webhook провайдера
│   │   ├── library/                # Dev 3 — купленные игры пользователя
│   │   ├── reviews/                 # Dev 3 — отзывы к играм
│   │   └── common/                   # общие пагинация/утилиты
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # Dev 4 — React SPA
│   └── src/
│       ├── pages/              # StorePage, GamePage, CartPage, LibraryPage, Login/Register
│       ├── components/          # Layout, GameCard, ...
│       ├── api/                  # axios-клиенты (catalog, store, auth)
│       └── store/                  # zustand (authStore)
└── docker-compose.yml         # mssql + backend + frontend одной командой
```

## Распределение работы

**Dev 1 (Backend) — `apps/accounts`**
Регистрация/логин (JWT через simplejwt), профиль `me/`, публичные профили, друзья. Точка роста: 2FA, восстановление пароля, email-верификация.

**Dev 2 (Backend) — `apps/catalog`**
Модели Game/Genre/Tag/Screenshot/SystemRequirement, витрина с фильтрами и поиском (django-filter + SearchFilter), админка для загрузки контента. Точка роста: региональные цены, рекомендации, DLC/бандлы.

**Dev 3 (Backend) — `apps/store`, `apps/payments`, `apps/library`, `apps/reviews`**
Корзина → checkout → Order → Payment → webhook → зачисление в Library. Отзывы с привязкой к владению игрой. Точка роста: скидки/промокоды, возвраты (refund), подарки друзьям.

**Dev 4 (Frontend) — весь `frontend/`**
React Router (витрина/игра/корзина/библиотека/профиль/авторизация), React Query для запросов к API, zustand для JWT-токенов, Tailwind для стилей. Точка роста: региональная витрина, live-поиск, страница профиля с достижениями/отзывами.

## Как поднять локально

```bash
docker compose up --build
```
- Backend: http://localhost:8000/api/docs/ (Swagger)
- Frontend: http://localhost:5173
- MSSQL: localhost:1433 (sa / YourStrong!Passw0rd)

Первый запуск бэкенда:
```bash
docker compose exec backend python manage.py createsuperuser
```

## Что дальше (не входит в скелет, но понадобится)

- Реальная интеграция платёжного провайдера (Stripe/LiqPay) в `apps/payments`
- Хранение файлов (скриншоты, установочные архивы) — S3/MinIO вместо локального `media/`
- Полнотекстовый поиск / Elasticsearch, если каталог вырастет
- CI (lint + tests) — GitHub Actions, тесты через `pytest-django`
- Разделение на региональные цены и НДС по `country_code` пользователя

## Важное про MSSQL

Драйвер — `mssql-django` (+ `pyodbc` + ODBC Driver 18, уже в `backend/Dockerfile`). Модели используют `UUIDField` как PK — MSSQL это поддерживает, но проверяйте план миграций перед продакшеном (индексы на UUID работают иначе, чем на INT IDENTITY — при большом объёме данных возможно стоит перейти на `BigAutoField` + отдельный `public_id`).
