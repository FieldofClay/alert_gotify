import sys, requests, json, re

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def check_inputs(config):
    setup_fields = ['url', 'token']
    required_fields = ['message', 'priority']
    
    for field in setup_fields:
        if not field in config:
            eprint("ERROR No "+field+" specified. Have you configured the addon?")
            return False
    
    for field in required_fields:
        if not field in config:
            eprint("ERROR, No "+field+" specified.")
            return False
        
    return True


if len(sys.argv) > 1 and sys.argv[1] == "--execute":
    alert = json.load(sys.stdin)
    if check_inputs(alert['configuration']):
        #load config
        config = alert['configuration']
        ssl_verify = True
        if 'ssl_verify' in config:
            if config['ssl_verify'] in ['false', 'False', 'FALSE']:
                ssl_verify = False

        #construct headers
        headers = {'X-Gotify-Key': config['token'], 'accept': 'application/json', 'Content-Type': 'application/json'}

        #construct payload
        payload = {}
        if 'title' in config:
            payload['title'] = config['title']
        payload['message'] = config['message']
        payload['priority'] = int(config['priority'])

        #url
        url = config['url']
        if url[-1] == "/":
            url = url[:-1]
        url += "/message"

        #doit
        r = requests.post(url,headers=headers,json=payload,verify=ssl_verify)
        if r.status_code == 200:
            eprint("INFO 200: Success sending message")
        else:
            eprint("ERROR "+str(r.status_code)+": "+r.text)

    else:
        eprint("ERROR Invalid configuration detected. Stopped.")
else:
    eprint("FATAL No execute flag given")
