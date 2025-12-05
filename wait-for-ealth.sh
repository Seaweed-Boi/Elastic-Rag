#!/usr/bin/env bash
set -e
TARGET=${1:-http://127.0.0.1:8000/ready}
RETRIES=${2:-60}
SLEEP=${3:-1}
echo "Waiting for $TARGET (retries=$RETRIES)..."
i=0
while [ $i -lt "$RETRIES" ]; do
  if curl -fsS "$TARGET" >/dev/null 2>&1; then
    echo "OK: $TARGET is healthy"
    exit 0
  fi
  i=$((i+1))
  echo "Health not ready, attempt ${i}/${RETRIES}"
  sleep "$SLEEP"
done
echo "ERROR: $TARGET not healthy after ${RETRIES} attempts" >&2
exit 1
