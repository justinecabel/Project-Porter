#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


APPS_PATH = Path(os.environ.get("APPS_PATH", "/etc/nginx/config/apps.json"))


def fail(message):
    print(f"init-apps-json: {message}", file=sys.stderr)
    sys.exit(1)


def get_required(name):
    value = os.environ.get(name)
    if value is None or value == "":
        fail(f"missing required environment variable {name}")
    return value


def main():
    if APPS_PATH.exists():
        print(f"using existing {APPS_PATH}")
        return

    try:
        app_count = int(os.environ.get("APP_COUNT", "0"))
    except ValueError:
        fail("APP_COUNT must be a number")

    if app_count < 1:
        fail("APP_COUNT must be at least 1")

    apps = []
    for index in range(1, app_count + 1):
        prefix = f"APP_{index}"
        try:
            port = int(get_required(f"{prefix}_PORT"))
        except ValueError:
            fail(f"{prefix}_PORT must be a number")

        apps.append({
            "name": get_required(f"{prefix}_NAME"),
            "route": get_required(f"{prefix}_ROUTE"),
            "host": get_required(f"{prefix}_HOST"),
            "port": port,
        })

    APPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPS_PATH.write_text(json.dumps({"apps": apps}, indent=2) + "\n")
    print(f"created {APPS_PATH} from Compose environment")


if __name__ == "__main__":
    main()
