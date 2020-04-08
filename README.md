## Gotify Alert Action
Adds an alert action to Splunk that sends a message to a Gotify server. 

This add-on requires a [Gotify server](https://github.com/gotify/server") to function.

Before using this add-on, it needs to be configured in Splunk. This can be done in the Splunk UI under *Settings>Alert Actions>Setup Gotify Alert Action*. Alternatively, this can be done by updating and placing the below config in local/alert_actions.conf

    [gotify_message]
    param.server = <<URL>>
    param.token = <<APP_TOKEN>>
