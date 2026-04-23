# Deployment Guide

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure environment

1. Copy `.env.example` to `.env`.
2. Set production-safe values.
3. Ensure `DJANGO_DEBUG=False`.

## 3. Apply database migrations

```bash
python manage.py migrate
```

## 4. Collect static files

```bash
python manage.py collectstatic --noinput
```

## 5. Run health checks

```bash
python manage.py check --deploy
python manage.py test
```

## 6. Start app server

```bash
gunicorn config.wsgi --log-file -
```

## Recommended production environment variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_PRELOAD=True`
- `CSRF_TRUSTED_ORIGINS`

## Notes

- Keep `MEDIA_ROOT` on persistent storage.
- Use HTTPS termination at load balancer/reverse proxy.
- Ensure proxy passes `X-Forwarded-Proto`.
