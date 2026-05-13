# Tailscale Funnel NGINX Reverse Proxy

This project runs NGINX in Docker Compose and keeps Tailscale Funnel on the host.
NGINX listens on host port `80`; Funnel can then publish that local service.

## Files

- `docker-compose.yml` runs the reverse proxy container on port `80`.
- `config/apps.json` defines your local proxied apps by `name`, `route`, `host`, and `port`.
- `apps.example.json` is a safe example file to commit and copy from.
- `nginx/templates/nginx.conf.template` provides the server template.
- `scripts/init-apps-json.py` creates `config/apps.json` on first run from Compose environment variables.
- `scripts/generate-nginx-config.py` renders NGINX config from `config/apps.json`.
- `scripts/start.sh` starts NGINX and reloads it when config inputs change.

## Configure Apps

On first run, the container creates `config/apps.json` from the app variables in
`docker-compose.yml`:

```yaml
environment:
  APP_COUNT: ${APP_COUNT:-2}
  APP_1_NAME: ${APP_1_NAME:-app-3001}
  APP_1_ROUTE: ${APP_1_ROUTE:-/app1/}
  APP_1_HOST: ${APP_1_HOST:-host.docker.internal}
  APP_1_PORT: ${APP_1_PORT:-3001}
  APP_2_NAME: ${APP_2_NAME:-vite-app}
  APP_2_ROUTE: ${APP_2_ROUTE:-/app2/}
  APP_2_HOST: ${APP_2_HOST:-host.docker.internal}
  APP_2_PORT: ${APP_2_PORT:-5173}
```

That produces:

```json
{
  "apps": [
    {
      "name": "app-3001",
      "route": "/app1/",
      "host": "host.docker.internal",
      "port": 3001
    },
    {
      "name": "vite-app",
      "route": "/app2/",
      "host": "host.docker.internal",
      "port": 5173
    }
  ]
}
```

After the first run, edit `config/apps.json` directly. It is ignored by Git so
local app names, routes, hostnames, and ports are not shared on GitHub.

If you want to regenerate it from Compose environment defaults, delete
`config/apps.json` and restart the container.

You can also create it from the host before starting Docker:

```bash
APPS_PATH=config/apps.json python3 scripts/init-apps-json.py
```

Routes are unique path prefixes. A route such as `/api/` proxies to the root of
the upstream app at `http://host.docker.internal:3000/`.

Use `host.docker.internal` for apps running on the host machine. Use a Docker
Compose service name for apps running on the same Compose network.

## Run

```bash
docker compose up -d --build
```

After editing `config/apps.json`, the running container regenerates NGINX config,
validates it with `nginx -t`, and reloads NGINX automatically.

## Publish With Tailscale Funnel

Run Funnel on the host machine:

```bash
sudo tailscale funnel 80
```

Tailscale remains outside Docker; the container only serves HTTP on local port
`80`.
