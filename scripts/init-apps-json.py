#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


APPS_PATH = Path(os.environ.get("APPS_PATH", "/etc/nginx/config/apps.json"))
DEFAULT_APPS = [
    {
        "name": "app-3001",
        "route": "/app1/",
        "host": "host.docker.internal",
        "port": 3001,
    },
    {
        "name": "vite-app",
        "route": "/",
        "host": "host.docker.internal",
        "port": 5173,
    },
]


def fail(message):
    print(f"init-apps-json: {message}", file=sys.stderr)
    sys.exit(1)


def get_required(name, default=None):
    value = os.environ.get(name, default)
    if value is None or value == "":
        fail(f"missing required environment variable {name}")
    return value


def default_app_value(index, key):
    try:
        return DEFAULT_APPS[index - 1][key]
    except IndexError:
        return None


def main():
    if APPS_PATH.is_dir():
        fail(f"{APPS_PATH} is a directory; remove it and rerun this command")

    if APPS_PATH.exists():
        print(f"using existing {APPS_PATH}")
        return

    try:
        app_count = int(os.environ.get("APP_COUNT", str(len(DEFAULT_APPS))))
    except ValueError:
        fail("APP_COUNT must be a number")

    if app_count < 1:
        fail("APP_COUNT must be at least 1")

    apps = []
    for index in range(1, app_count + 1):
        prefix = f"APP_{index}"
        try:
            port = int(get_required(f"{prefix}_PORT", default_app_value(index, "port")))
        except ValueError:
            fail(f"{prefix}_PORT must be a number")

        apps.append({
            "name": get_required(f"{prefix}_NAME", default_app_value(index, "name")),
            "route": get_required(f"{prefix}_ROUTE", default_app_value(index, "route")),
            "host": get_required(f"{prefix}_HOST", default_app_value(index, "host")),
            "port": port,
        })

    APPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPS_PATH.write_text(json.dumps({"apps": apps}, indent=2) + "\n")
    print(f"created {APPS_PATH} from Compose environment")


if __name__ == "__main__":
    main()
