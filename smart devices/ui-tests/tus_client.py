# WiKi: https://wiki.yandex-team.ru/test-user-service/
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tus_base_url = 'https://tus.yandex-team.ru/1'
env = 'prod'
consumer = 'yandex_tv'


def init_account(config):
    from retrying import retry

    @retry(wait_exponential_multiplier=5000, wait_exponential_max=60000)
    def _init():
        url = f'{tus_base_url}/get_account/'
        headers = {"Authorization": f'OAuth {config["tus_token"]}',
                   "Content-Type": 'application/x-www-form-urlencoded'}
        response = requests.get(url=f'{tus_base_url}/get_account/',
                                data={"env": env,
                                      "tus_consumer": consumer,
                                      "uid": config["tus_account_uid"]},
                                headers=headers,
                                verify=False)
        if response.ok:
            config["ya_login"] = response.json()['account']['login']
            config["ya_pass"] = response.json()['account']['password']
            return response
        else:
            raise RuntimeError("Invalid response from tus\n url: %s,\n code: %s,\n body: %s."
                               % (url, response.status_code, response.json()))
    return _init()
