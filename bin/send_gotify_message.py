import sys, requests, json, re, os
import logging, logging.handlers
import splunk

def setup_logging():
    logger = logging.getLogger('splunk.gotify')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "gotify.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger


def check_inputs(config, logger):
    setup_fields = ['url', 'token']
    required_fields = ['message', 'priority']
    
    for field in setup_fields:
        if not field in config:
            logger.error("No "+field+" specified. Have you configured the addon?")
            return False
    
    for field in required_fields:
        if not field in config:
            logger.error("No "+field+" specified.")
            return False
        
    return True


if len(sys.argv) > 1 and sys.argv[1] == "--execute":
    logger = setup_logging()
    alert = json.load(sys.stdin)
    if check_inputs(alert['configuration'], logger):
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
            logger.info("200: Success sending message")
        else:
            logger.error(str(r.status_code)+": "+r.text)

    else:
        logger.error("Invalid configuration detected. Stopped.")
else:
    print("FATAL No execute flag given")
