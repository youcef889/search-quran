# Deployment Runbook

## Stack

| Component | Detail |
| --- | --- |
| Image base | `python:3.13.3-slim-bookworm` |
| WSGI server | Gunicorn — compose runs `--workers 4 --bind 0.0.0.0:4000 app:app` |
| Reverse proxy | `nginx:alpine`, ports 80 + 443 |
| TLS | Certbot (volumes `./certbot/conf`, `./certbot/www`) |
| Network | bridge network `quran` (web exposes 4000 internally, not published) |
| Domain | `xmpp.linuxjourney.blog` |
| Secrets | `.env` (git-ignored), passed to `web` via `env_file` |

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000, debug=True
```

## Tests

```bash
pytest
```

See [testing.md](testing.md).

## Production

### With Docker Compose (canonical)

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

- `web` — builds the Dockerfile, runs Gunicorn on 4000, reads `.env`.
- `nginx` — proxies to `quran-app:4000`, mounts config read-only:
  - `./nginx/conf.d` → `/etc/nginx/conf.d:ro`
  - `./certbot/www` → `/var/www/certbot:ro`
  - `./certbot/conf` → `/etc/letsencrypt:ro`
  - `./nginx-logs` → `/var/log/nginx`

### Without Compose

```bash
docker build -t quran-app .
docker run -p 4000:4000 --env-file .env quran-app
# or directly:
gunicorn --bind 0.0.0.0:4000 app:app
```

## Nginx

`nginx/conf.d/quran.conf` proxies `/` to `http://quran-app:4000`, forwarding
`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` with 60s connect/read
timeouts. Reload after any change:

```bash
docker compose exec nginx nginx -t && docker compose exec nginx nginx -s reload
```

## TLS certificates (Certbot)

Certificates are stored in `./certbot/conf` and challenges served from `./certbot/www`.
Renewal:

```bash
docker compose run --rm certbot renew --webroot -w /var/www/certbot
docker compose exec nginx nginx -s reload
```

Schedule renewal (certbot renewals are safe to run twice a day; add a cron entry on the
host if not already present).

## Rollback

```bash
git checkout <previous-commit>
docker compose up -d --build
```

Data files are baked into the image; there is no database to migrate.

## Health check

```bash
curl -fsS http://localhost:4000/ >/dev/null && echo OK     # from inside the host
curl -fsSI https://xmpp.linuxjourney.blog/                  # public TLS + proxy path
```

## Logs

| Where | How |
| --- | --- |
| Application | stdout/stderr → `docker compose logs -f web` (format `%(asctime)s %(levelname)s %(name)s %(message)s`) |
| Nginx | `./nginx-logs/access.log`, `./nginx-logs/error.log` (bind-mounted) |

## Post-deploy checklist

1. `/` renders 114 surahs over HTTPS.
2. `/surah/1` and `/surah/1?verse=7` render with context.
3. `/search?q=بسم الله` and `/search/passage?q=...` return results.
4. `/nonexistent` returns the custom 404 page.
5. Security headers present (`curl -I`).
6. Certificate valid (`echo | openssl s_client -servername ... | openssl x509 -noout -dates`).
