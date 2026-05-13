#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path


APPS_PATH = Path(os.environ.get("APPS_PATH", "/etc/nginx/config/apps.json"))
TEMPLATE_PATH = Path(os.environ.get("TEMPLATE_PATH", "/etc/nginx/templates/nginx.conf.template"))
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", "/etc/nginx/conf.d/default.conf"))

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def fail(message):
    print(f"generate-nginx-config: {message}", file=sys.stderr)
    sys.exit(1)


def load_apps():
    try:
        raw = json.loads(APPS_PATH.read_text())
    except FileNotFoundError:
        fail(f"missing {APPS_PATH}; it should be generated on first startup")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {APPS_PATH}: {exc}")

    apps = raw.get("apps")
    if not isinstance(apps, list):
        fail('"apps" must be a list')

    return apps


def normalize_route(route):
    if not isinstance(route, str) or not route.startswith("/"):
        fail("each app route must be a string starting with /")

    if "?" in route or "#" in route:
        fail(f"route {route!r} must not contain query strings or fragments")

    if route != "/" and not route.endswith("/"):
        route += "/"

    return route


def validate_app(app):
    if not isinstance(app, dict):
        fail("each app must be an object")

    name = app.get("name")
    route = normalize_route(app.get("route"))
    host = app.get("host")
    port = app.get("port")

    if not isinstance(name, str) or not NAME_RE.match(name):
        fail("each app name must contain only letters, numbers, dots, underscores, or dashes")

    if not isinstance(host, str) or not HOST_RE.match(host):
        fail(f"app {name!r} has an invalid host")

    try:
        port = int(port)
    except (TypeError, ValueError):
        fail(f"app {name!r} has an invalid port")

    if port < 1 or port > 65535:
        fail(f"app {name!r} has an invalid port")

    return {
        "name": name,
        "route": route,
        "host": host,
        "port": port,
    }


def render_location(app):
    route = app["route"]
    upstream = f"http://{app['host']}:{app['port']}"

    if route == "/":
        proxy_pass = f"{upstream};"
    else:
        proxy_pass = f"{upstream}/;"

    return f"""    # {app['name']}
    location {route} {{
        proxy_pass {proxy_pass}
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Port $server_port;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }}"""


def main():
    apps = [validate_app(app) for app in load_apps()]

    routes = [app["route"] for app in apps]
    if len(routes) != len(set(routes)):
        fail("routes must be unique")

    locations = "\n\n".join(render_location(app) for app in apps)

    template = TEMPLATE_PATH.read_text()
    config = """map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

""" + template.replace("{{ locations }}", locations)

    OUTPUT_PATH.write_text(config)
    print(f"generated {OUTPUT_PATH} for {len(apps)} app(s)")


if __name__ == "__main__":
    main()
