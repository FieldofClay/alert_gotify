#!/bin/bash
set -e

TIMEOUT=${1:-180}
CHECK_INTERVAL=5

echo "=== Gotify Integration Test Verification ==="
echo "Timeout: ${TIMEOUT}s"
echo "Checking for successful message delivery to Gotify..."
echo ""

start_time=$(date +%s)

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    if [ $elapsed -ge $TIMEOUT ]; then
        echo ""
        echo "TIMEOUT: No successful message delivery after ${TIMEOUT}s"
        echo ""
        echo "=== Docker Container Status ==="
        docker compose ps
        echo ""
        echo "=== Gotify Logs ==="
        docker compose logs gotify
        echo ""
        echo "=== Splunk Logs (last 100 lines) ==="
        docker compose logs --tail=100 splunk | grep -i "gotify\|alert" || docker compose logs --tail=100 splunk
        echo ""
        exit 1
    fi
    
    # Check Gotify logs for 200 POST to /message endpoint
    LOGS=$(docker compose logs gotify 2>/dev/null || echo "")
    
    # Look for: 2025-10-16T02:24:59Z | 200 |   59.458697ms | 2001:cafe:42::6c0 | POST     "/message?token=[masked]"
    if echo "$LOGS" | grep -E '200.*POST.*"/message' > /dev/null; then
        echo ""
        echo "SUCCESS: Message successfully delivered to Gotify!"
        echo ""
        echo "=== Delivery Confirmation ==="
        echo "$LOGS" | grep -E '200.*POST.*"/message"' | tail -5
        echo ""
        echo "=== Splunk Alert Logs ==="
        docker compose logs splunk | grep -i "gotify\|alert_gotify\|200: Success" | tail -20 || echo "No detailed logs found"
        echo ""
        echo "Integration test PASSED in ${elapsed}s"
        exit 0
    fi
    
    echo -n "."
    sleep $CHECK_INTERVAL
done
