# Integration Tests for alert_gotify

End-to-end integration tests that verify the alert_gotify add-on works correctly with Splunk and Gotify.

## Architecture

```
┌──────────┐         ┌─────────────┐         ┌─────────┐
│  Splunk  │────────>│ alert_gotify│────────>│ Gotify  │
│  (Alert) │         │   (Add-on)  │         │ (Server)│
└──────────┘         └─────────────┘         └─────────┘
```

## Components

### Docker Services

1. **gotify** - Gotify server instance
   - Default admin credentials: admin/admin
   - Accessible at `http://gotify` within the Docker network

2. **gotify-init** - One-time initialization container
   - Creates a test application in Gotify via API
   - Stores app token in shared volume for Splunk to use
   - Exits after successful initialization

3. **splunk** - Splunk Enterprise instance
   - Has alert_gotify add-on mounted
   - Configured with a scheduled search that triggers every minute
   - Reads Gotify credentials from shared volume

### Test Flow

1. **Build**: UCC framework builds the alert_gotify add-on
2. **Start**: Docker Compose starts Gotify and Splunk containers
3. **Initialize**: `init-gotify.sh` creates Gotify app and saves token
4. **Configure**: `configure-splunk.sh` configures Splunk alert with token
5. **Execute**: Splunk runs scheduled search every minute
6. **Alert**: alert_gotify sends message to Gotify
7. **Verify**: `verify.sh` checks Gotify logs for successful 200 POST
8. **Cleanup**: Docker Compose tears down all services

## Files

- **docker-compose.yml** - Defines Gotify, init container, and Splunk services
- **init-gotify.sh** - Creates Gotify application and stores token
- **configure-splunk.sh** - Configures Splunk with Gotify credentials
- **splunk_config/savedsearches.conf.template** - Alert configuration template
- **verify.sh** - Verification script that checks for successful delivery

## Running Locally

### Prerequisites

- Docker and Docker Compose installed
- UCC framework installed: `pip install splunk-add-on-ucc-framework`

### Steps

```bash
# 1. Build the add-on
cd /path/to/alert_gotify
ucc-gen build --source alert_gotify/package --ta-version 0.0.1-test

# 2. Make scripts executable
cd alert_gotify/tests/integration
chmod +x verify.sh init-gotify.sh configure-splunk.sh

# 3. Start services
docker compose up -d

# 4. Run verification (waits up to 240 seconds)
./verify.sh 240

# 5. Cleanup
docker compose down -v
```

### Testing Different Splunk Versions

```bash
# Test with Splunk 9.1
SPLUNK_VERSION=9.1 docker compose up -d

# Test with Splunk 10.0
SPLUNK_VERSION=10.0 docker compose up -d
```

## Verification

The test looks for this pattern in Gotify container logs:

```
2025-10-16T02:24:59Z | 200 |   59.458697ms | 2001:cafe:42::6c0 | POST     "/message?token=[masked]"
```

This confirms:
- ✅ Alert triggered successfully
- ✅ Message sent to Gotify API
- ✅ Gotify received and processed message (200 status)
- ✅ End-to-end flow working

## Troubleshooting

### Check if services are running

```bash
docker compose ps
```

### View Gotify logs

```bash
docker compose logs gotify
```

### View Splunk logs

```bash
docker compose logs splunk | grep -i gotify
docker compose logs splunk | grep -i alert
```

### Check Gotify token creation

```bash
docker compose logs gotify-init
```

### Verify token file exists

```bash
docker compose exec splunk cat /gotify-data/gotify_token.txt
```

### Access Gotify UI

While containers are running:
- Gotify is not exposed on host (internal network only)
- To expose: Add `ports: - 8080:80` to gotify service

### Access Splunk UI

While containers are running:
```
URL: http://localhost:8000
Username: admin
Password: who_rocks?
```

## CI/CD Integration

The `.github/workflows/integration-test.yml` workflow:
- Runs on push/PR to main branch
- Tests multiple Splunk versions (9.0, 9.1, 9.2, 10.0)
- Builds add-on fresh for each test
- Runs full integration test
- Reports success/failure

## Common Issues

**Problem**: Timeout waiting for message delivery

**Solutions**:
- Check if Splunk started successfully: `docker compose logs splunk`
- Verify alert is enabled: Check savedsearches.conf was created
- Check alert_gotify logs: `docker compose logs splunk | grep alert_gotify`

**Problem**: Token not found

**Solutions**:
- Check init container: `docker compose logs gotify-init`
- Verify Gotify is healthy: `docker compose ps`
- Check token file exists: `docker exec splunk ls -la /gotify-data/`

**Problem**: Message not reaching Gotify

**Solutions**:
- Check network connectivity: `docker compose exec splunk ping gotify`
- Verify URL and token in savedsearches.conf
- Check Splunk alert execution logs
