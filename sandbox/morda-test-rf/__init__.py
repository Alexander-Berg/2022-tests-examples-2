import json
import logging
import re
import requests
import time

from sandbox import sdk2
from sandbox.sdk2 import yav
import sandbox.projects.common.environments as env

USER_AGENT = 'Mozilla/5.0 (Linux; x86; Android 11; sdk_gphone_x86) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.216 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/21.51.1'
PUSH_AGENT_URL = 'http://portal-yasm.wdevx.yandex.ru:11005'


def get_flag_url(flag_name):
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
    })

    response = session.get(
        'http://yabs.yandex.ru/page/278239?clid=0&device-class=android&enabled_features=ya_plus%0Aaccount%0Apush_system_settings%0Adisk%0Asearchbar%0Awidget_update&lang=ru&mobilmail=0&options={}&sids=2%0A16%0A42%0A59%0A73&tablet=0&tune-region-id=213&uid=1525894689&uuid=6df590aa378547b5bec9ef20535e14fd'.format(flag_name)
    )
    if response.status_code != 200:
        logging.info('Failed to send get request. Response status_code={}'.format(response.status_code))
        return None
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))
        logging.info(response.json())

    data = None
    if response.json() and response.json().get('data', None):
        data = response.json().get('data', None)
    else:
        return None

    linkhead = None
    if data.get('linkhead'):
        linkhead = data.get('linkhead', None)
    else:
        return None

    logging.info('linkhead')
    logging.info(linkhead)

    found_flag = False
    linknext = None
    options = data.get('options', None)
    if options:
        for option in options:
            logging.info(option)
            code = option.get('code', None)
            bs_data = option.get('bs_data', None)
            if bs_data is not None:
                if option.get('direct_data').get('option') == flag_name:
                    linknext = bs_data.get('count_links').get('linkTail')
                    found_flag = True
            elif code is not None:
                if code.get('flag') == flag_name:
                    linknext = option.get('linknext')
                    found_flag = True

    logging.info('found_flag')
    logging.info(found_flag)
    logging.info('linknext')
    logging.info(linknext)

    if found_flag == False:
        return None
    if linknext == None:
        return None

    return linkhead + linknext

def rf_for_url_works(url, flag_name):
    logging.info('Url = ')
    logging.info(url)

    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
    })
    response = session.get(
        url
    )
    if response.status_code != 200:
        logging.info('Failed to send get request. Response status_code={}'.format(response.status_code))
        return False
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))

    time.sleep(60)
    url = get_flag_url(flag_name)
    logging.info('Url = ')
    logging.info(url)
    if url == None:
        return True
    else:
        return False

def send_yasm_signal(signal_value):
    logging.info('send_yasm_signal')
    logging.info(signal_value)
    values = [{'name': 'api_search_rf_works_tttt', 'val': signal_value}]
    data = [{
        'ttl': 15000,
        'tags': {
            'itype': 'mordaschema'
        },
        'values': values
    }]
    logging.info('Sending yasm signals:\n' + json.dumps(data, indent=4))
    response = requests.post(
        url=PUSH_AGENT_URL,
        json=data,
        timeout=5
    )
    if response.status_code != 200:
        logging.info('Failed to send yasm metrics. Response status_code={}'.format(response.status_code))
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))

class MordaTestRf(sdk2.Task):
    """ Checking rf for api android """
    class Parameters(sdk2.Task.Parameters):
        flag_name = sdk2.parameters.String('BK flag name (api_android_test_rf_<1-6>)', default=None)

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 512
        disk_space = 100

    def on_execute(self):
        # Get yabs response
        flag_name = self.Parameters.flag_name
        url = get_flag_url(flag_name)
        if url == None:
            send_yasm_signal(0)
        elif rf_for_url_works(url, flag_name):
            send_yasm_signal(1)
        else:
            send_yasm_signal(0)
