#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "Starting OPOlogy COMPLETE Subject Notebook"
echo "Build: 2026-08-07 V9"
echo "Address: http://127.0.0.1:9012"
if command -v python3 >/dev/null 2>&1; then
  python3 opology_server.py --port 9012 --open
else
  echo "Python 3 is required. Install it from https://www.python.org/downloads/"
  read -r -p "Press Return to close."
fi
