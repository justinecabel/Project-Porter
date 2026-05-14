#!/usr/bin/env python3
from pathlib import Path


ENV_PATH = Path(".env")
DEFAULT_CONTENT = """# Local Docker Compose overrides for Project-Porter
NGINX_PORT=81
"""


def main():
    if ENV_PATH.exists():
        print(f"using existing {ENV_PATH}")
        return

    ENV_PATH.write_text(DEFAULT_CONTENT)
    print(f"created {ENV_PATH} with NGINX_PORT=81")


if __name__ == "__main__":
    main()
