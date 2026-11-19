#!/usr/bin/env bash
# ./run.sh [build|prices|serve|all]
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}
case "${1:-build}" in
  prices) $PY scripts/refresh_prices.py ;;
  build)  $PY scripts/build.py && $PY scripts/check_links.py ;;
  serve)  $PY scripts/build.py && mkdir -p /tmp/gta6-srv && rm -rf /tmp/gta6-srv/gta6-setup && cp -r dist /tmp/gta6-srv/gta6-setup && $PY -m http.server "${PORT:-8788}" -d /tmp/gta6-srv ;;
  all)    $PY scripts/refresh_prices.py && $PY scripts/build.py && $PY scripts/check_links.py ;;
  *) echo "usage: ./run.sh [build|prices|serve|all]"; exit 1 ;;
esac
