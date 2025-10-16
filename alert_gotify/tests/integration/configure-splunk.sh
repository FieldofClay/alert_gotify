#!/bin/bash
set -e

echo "Configuring Splunk with Gotify credentials..."

# Wait for token file to be available
TIMEOUT=60
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

# Create test_alert app directory
mkdir -p /opt/splunk/etc/apps/test_alert/local

# Copy savedsearches.conf template and substitute the token
cat /tmp/splunk_config/savedsearches.conf.template | \
  sed "s|{{GOTIFY_URL}}|${GOTIFY_URL}|g" | \
  sed "s|{{GOTIFY_TOKEN}}|${GOTIFY_TOKEN}|g" \
  > /opt/splunk/etc/apps/test_alert/local/savedsearches.conf

echo "Splunk configuration complete!"
echo "Alert will trigger every minute"
