#Options for Gotify Alert Action

action.gotify_message = [0|1]
* Enable Gotify Alert Action

action.gotify_message.param.url = <string>
* Override global url of your Gotify server
* (optional)

action.gotify_message.param.token = <string>
* Override global app token to use
* (optional)

action.gotify_message.param.title = <string>
* Message title
* (optional)

action.gotify_message.param.message = <string>
* Message content
* (required)

action.gotify_message.param.priority = [0-10]
* Message priority. 0=Min, 1-3=Low, 3-7=Normal, >7=High
* (required)
