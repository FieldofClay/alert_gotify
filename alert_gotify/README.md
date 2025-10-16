## Gotify Alert Action
Adds an alert action to Splunk that sends a message to a Gotify server. 

This add-on requires a [Gotify server](https://github.com/gotify/server) to function.

## Configuration

### Global Settings (Required)

Configure default Gotify server settings via the Splunk UI:
1. Navigate to **Apps > Gotify Alert Action > Configuration**
2. Set the **Gotify Server URL** (e.g., `https://gotify.example.com`)
3. Set the **Gotify App Token** (stored encrypted)

Alternatively, configure via `local/alert_gotify_settings.conf`:

```ini
[settings]
gotify_url = https://gotify.example.com
gotify_token = your_app_token_here
```

### Alert Action Configuration

When creating an alert, the UI will show:
- **Message**: The notification message body (required)
- **Title**: Optional title for the notification
- **Priority**: Message priority from 0 (lowest) to 10 (highest), default is 5

### Advanced: Per-Alert Overrides (via Configuration Files)

You can override the global settings for specific alerts by manually editing configuration files. These parameters are **not visible in the UI** but are fully supported:

In `local/savedsearches.conf`:

```ini
[Your Alert Name]
# ... other alert settings ...
action.alert_gotify = 1
action.alert_gotify.param.message = Alert triggered!
action.alert_gotify.param.title = My Custom Alert
action.alert_gotify.param.priority = 8
# Optional overrides (not in UI):
action.alert_gotify.param.url = https://different-gotify-server.com
action.alert_gotify.param.token = different_app_token
action.alert_gotify.param.ssl_verify = 0
```

**Available hidden parameters:**
- `url`: Override the global Gotify server URL for this alert
- `token`: Override the global app token for this alert
- `ssl_verify`: Set to `0` to disable SSL certificate verification, `1` to enable (default)

## Usage

1. Create or edit a saved search in Splunk
2. Under "Alert Actions", select "Send a Gotify Message"
3. Configure message, title, and priority
4. Save the alert

The alert will use the global URL and token unless overridden in configuration files.
