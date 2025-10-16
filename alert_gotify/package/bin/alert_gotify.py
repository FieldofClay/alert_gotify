# encoding = utf-8
import os
import import_declare_test
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunktaucclib.alert_actions_base import ModularAlertBase
from alert_gotify import modalert_alert_gotify_helper

class AlertActionWorkeralert_gotify(ModularAlertBase):

    def __init__(self, ta_name, alert_name):
        super(AlertActionWorkeralert_gotify, self).__init__(ta_name, alert_name)

    def validate_params(self):
        # Message is required (enforced by UI)
        if not self.get_param("message"):
            self.log_error('message is a mandatory parameter, but its value is None.')
            return False
        
        # Priority is required (enforced by UI)
        if not self.get_param("priority"):
            self.log_error('priority is a mandatory parameter, but its value is None.')
            return False
        
        # URL and token can come from either alert config file or global settings
        # Note: url, token, and ssl_verify are not in the UI but can be set in savedsearches.conf
        url = self.get_param("url")
        token = self.get_param("token")
        global_url = self.get_global_setting("gotify_url")
        global_token = self.get_global_setting("gotify_token")
        
        if not url and not global_url:
            self.log_error("Gotify server URL must be specified either in the alert configuration file or in global settings.")
            return False
        
        if not token and not global_token:
            self.log_error("Gotify app token must be specified either in the alert configuration file or in global settings.")
            return False
        
        return True

    def process_event(self, *args, **kwargs):
        status = 0
        try:
            if not self.validate_params():
                return 3
            status = modalert_alert_gotify_helper.process_event(self, *args, **kwargs)
        except (AttributeError, TypeError) as ae:
            self.log_error("Error: {}. Please double check spelling and also verify that a compatible version of Splunk_SA_CIM is installed.".format(str(ae)))
            return 4
        except Exception as e:
            msg = "Unexpected error: {}."
            if str(e):
                self.log_error(msg.format(str(e)))
            else:
                import traceback
                self.log_error(msg.format(traceback.format_exc()))
            return 5
        return status

if __name__ == "__main__":
    exitcode = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify").run(sys.argv)
    sys.exit(exitcode)
