#!/bin/sh
set -e

echo "Initializing Gotify and creating test application..."

# Install curl if not available
if ! command -v curl > /dev/null 2>&1; then
    echo "Installing curl..."
    apk add --no-cache curl
fi

# Wait for Gotify to be fully ready
sleep 5

# Create an application in Gotify
echo "Creating Gotify application..."
RESPONSE=$(curl -s -X POST "${GOTIFY_URL}/application" \
  -u "${GOTIFY_USER}:${GOTIFY_PASS}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Splunk Alert Test",
    "description": "Test application for Splunk alert_gotify integration tests"
  }')

# Extract the token
TOKEN=$(echo "$RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to create Gotify application"
  echo "Response: $RESPONSE"
  exit 1
fi

echo "Successfully created Gotify application"
echo "Token: ${TOKEN:0:8}..."

# Store the token in a shared volume for Splunk to read
echo "$TOKEN" > /data/gotify_token.txt
echo "${GOTIFY_URL}" > /data/gotify_url.txt

echo "Gotify initialization complete!"
