# Tailscale Funnel NGINX Reverse Proxy

This project runs NGINX in Docker Compose and keeps Tailscale Funnel on the host.
NGINX listens on host port `80`; Funnel can then publish that local service.

## Files

- `docker-compose.yml` runs the reverse proxy container on port `80`.
- `apps.json` defines proxied apps by `name`, `route`, `host`, and `port`.
- `nginx/templates/nginx.conf.template` provides the server template.
- `scripts/generate-nginx-config.py` renders NGINX config from `apps.json`.
- `scripts/start.sh` starts NGINX and reloads it when config inputs change.

## Configure Apps

Edit `apps.json`:

```json
{
  "apps": [
    {
      "name": "api",
      "route": "/api/",
      "host": "host.docker.internal",
      "port": 3000
    }
  ]
}
```

Routes are unique path prefixes. A route such as `/api/` proxies to the root of
the upstream app at `http://host.docker.internal:3000/`.

Use `host.docker.internal` for apps running on the host machine. Use a Docker
Compose service name for apps running on the same Compose network.

## Run

```bash
docker compose up -d --build
```

After editing `apps.json`, the running container regenerates NGINX config,
validates it with `nginx -t`, and reloads NGINX automatically.

## Publish With Tailscale Funnel

Run Funnel on the host machine:

```bash
sudo tailscale funnel 80
```

Tailscale remains outside Docker; the container only serves HTTP on local port
`80`.
