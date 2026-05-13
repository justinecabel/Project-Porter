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

On first run, the container creates `config/apps.json` from the defaults in
`scripts/init-apps-json.py`. That produces:

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
      "route": "/",
      "host": "host.docker.internal",
      "port": 5173,
      "proxy_host_header": "localhost:5173"
    }
  ]
}
```

After the first run, edit `config/apps.json` directly. It is ignored by Git so
local app names, routes, hostnames, and ports are not shared on GitHub.

If you want to regenerate it from the built-in defaults, delete
`config/apps.json` and restart the container.

You can also create it from the host before starting Docker:

```bash
APPS_PATH=config/apps.json python3 scripts/init-apps-json.py
```

Routes are unique path prefixes. A route such as `/api/` proxies to the root of
the upstream app at `http://host.docker.internal:3000/`.

For Vite or other frontend dev servers, configure the app with a matching base
path, such as `base: "/pm-ui/"`, and set `strip_prefix` to `false` so the app
receives the same path it was built for.

Some dev servers also restrict allowed hostnames. For apps running on your host,
set `host` to `host.docker.internal` so Docker can connect, and set
`proxy_host_header` to `localhost:<port>` so the dev server accepts the request.

If an app is not base-path aware and still emits root-relative assets like
`/src/main.js`, `extra_routes` can be used as a temporary development workaround:

```json
{
  "name": "pm-ui",
  "route": "/pm-ui/",
  "host": "host.docker.internal",
  "port": 5173,
  "proxy_host_header": "localhost:5173",
  "strip_prefix": false,
  "extra_routes": [
    "/stats",
    "/@vite/",
    "/src/",
    "/node_modules/",
    "/map-cache-sw.js"
  ]
}
```

Use `host.docker.internal` for apps running on the host machine. Use a Docker
Compose service name for apps running on the same Compose network.

## Windows Notes

`host.docker.internal` is the right hostname for apps running on your Windows
host through Docker Desktop. Inside the NGINX container, `localhost` means the
container itself, so Windows host apps should use:

```json
{
  "host": "host.docker.internal",
  "port": 5173
}
```

If `config/apps.json` was accidentally created as a folder, remove it and
regenerate it from PowerShell:

```powershell
docker compose down
Remove-Item -Recurse -Force .\config\apps.json
$env:APPS_PATH = "config/apps.json"
python scripts/init-apps-json.py
docker compose build --no-cache
docker compose up -d
```

The repository includes `.gitattributes` so shell scripts keep Linux `LF` line
endings when checked out on Windows.

## Run

```bash
docker compose up -d --build
```

After editing `config/apps.json`, the running container regenerates NGINX config,
validates it with `nginx -t`, and reloads NGINX automatically.

## Publish With Tailscale Funnel

Run Funnel on the host machine:

```bash
tailscale funnel --bg --https=443 http://127.0.0.1:80
```

Tailscale remains outside Docker; the container only serves HTTP on local port
`80`.
