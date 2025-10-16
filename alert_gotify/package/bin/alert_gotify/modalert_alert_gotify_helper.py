# encoding = utf-8
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import requests


def process_event(helper, *args, **kwargs):
    helper.log_info("Alert action alert_gotify started.")
    
    # Get parameters from alert configuration
    url = helper.get_param("url")
    token = helper.get_param("token")
    message = helper.get_param("message")
    title = helper.get_param("title")
    priority = helper.get_param("priority")
    ssl_verify = helper.get_param("ssl_verify")
    
    # Get global settings if alert-specific settings are not provided
    if not url:
        url = helper.get_global_setting("gotify_url")
        helper.log_info("Using global Gotify URL setting")
    
    if not token:
        token = helper.get_global_setting("gotify_token")
        helper.log_info("Using global Gotify token setting")
    
    # Handle SSL verification - default to True if not specified
    if ssl_verify is None or ssl_verify == "":
        ssl_verify = True
    elif isinstance(ssl_verify, str):
        ssl_verify = ssl_verify not in ['0', 'false', 'False', 'FALSE', 'no', 'No', 'NO']
    else:
        ssl_verify = bool(ssl_verify)
    
    try:
        # Construct headers
        headers = {
            'X-Gotify-Key': token,
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Construct payload
        payload = {
            'message': message,
            'priority': int(priority)
        }
        
        if title:
            payload['title'] = title
        
        # Construct URL
        gotify_url = url
        if gotify_url.endswith("/"):
            gotify_url = gotify_url[:-1]
        gotify_url += "/message"
        
        helper.log_info("Sending message to Gotify server: {}".format(url))
        
        # Send the request
        response = requests.post(
            gotify_url,
            headers=headers,
            json=payload,
            verify=ssl_verify
        )
        
        if response.status_code == 200:
            helper.log_info("Successfully sent Gotify message (200 OK)")
            return 0
        else:
            helper.log_error("Failed to send Gotify message. Status code: {}, Response: {}".format(
                response.status_code, response.text
            ))
            return 1
            
    except requests.exceptions.SSLError as e:
        helper.log_error("SSL verification failed: {}".format(str(e)))
        helper.log_error("Try setting 'Verify SSL Certificate' to false if using self-signed certificates")
        return 1
    except requests.exceptions.RequestException as e:
        helper.log_error("Request error sending Gotify message: {}".format(str(e)))
        return 1
    except Exception as e:
        helper.log_error("Error sending Gotify message: {}".format(str(e)))
        import traceback
        helper.log_error(traceback.format_exc())
        return 1
