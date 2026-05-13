#!/bin/sh
set -eu

APPS_PATH=/etc/nginx/apps.json
TEMPLATE_PATH=/etc/nginx/templates/nginx.conf.template
CHECK_INTERVAL="${CHECK_INTERVAL:-2}"

checksum() {
  sha256sum "$APPS_PATH" "$TEMPLATE_PATH" 2>/dev/null | sha256sum | awk '{print $1}'
}

reload_if_changed() {
  last_sum=""

  while true; do
    current_sum="$(checksum || true)"

    if [ -n "$current_sum" ] && [ "$current_sum" != "$last_sum" ]; then
      if generate-nginx-config && nginx -t; then
        if [ -n "$last_sum" ]; then
          nginx -s reload
          echo "reloaded nginx after config update"
        fi
        last_sum="$current_sum"
      else
        echo "config update failed; keeping previous nginx config" >&2
      fi
    fi

    sleep "$CHECK_INTERVAL"
  done
}

generate-nginx-config
nginx -t

reload_if_changed &
exec nginx -g "daemon off;"
