#!/bin/sh
set -e

echo "Configuring Splunk with Gotify credentials..."

# Wait for token file to be available
TIMEOUT=30
ELAPSED=0
while [ ! -f /gotify-data/gotify_token.txt ] && [ $ELAPSED -lt $TIMEOUT ]; do
  echo "Waiting for Gotify token..."
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done

if [ ! -f /gotify-data/gotify_token.txt ]; then
  echo "ERROR: Gotify token not found after ${TIMEOUT}s"
  exit 1
fi

# Read token and URL
GOTIFY_TOKEN=$(cat /gotify-data/gotify_token.txt)
GOTIFY_URL=$(cat /gotify-data/gotify_url.txt)

echo "Found Gotify credentials"
echo "URL: ${GOTIFY_URL}"
echo "Token: ${GOTIFY_TOKEN:0:8}..."

# Create output directory
OUTPUT_DIR=${OUTPUT_DIR:-/splunk-config}
mkdir -p "${OUTPUT_DIR}"

# Copy savedsearches.conf template and substitute the token
sed "s|{{GOTIFY_URL}}|${GOTIFY_URL}|g" /splunk_config/savedsearches.conf.template | \
  sed "s|{{GOTIFY_TOKEN}}|${GOTIFY_TOKEN}|g" \
  > "${OUTPUT_DIR}/savedsearches.conf"

echo "Splunk configuration written to ${OUTPUT_DIR}/savedsearches.conf"
echo "Alert will trigger every minute"
