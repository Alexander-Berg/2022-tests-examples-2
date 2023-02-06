import metrika.pylib.http as http


class TankError(Exception):
    pass


class Tank:
    def __init__(self,
                 host,
                 port,
                 ):
        self.host = host
        self.port = port
        self.headers = {
            'Charset': 'utf-8',
            'User-Agent': 'metrika-sandbox-load-testing',
        }
        self.base_url = 'http://{}:{}/api/v1'.format(host, port)

    def start_load_test(self, config):
        url = '{}/tests/start.json'.format(self.base_url)
        response = http.request(
            url,
            method='POST',
            files={'load.conf': config},
            headers=self.headers,
        ).json()
        if not response['success']:
            raise TankError('Unsuccessful tank response: {}'.format(response))
        return response['id']

    def get_load_test_status(self, load_test_id):
        url = '{}/tests/{}/status.json'.format(self.base_url, load_test_id)
        response = http.request(url).json()
        if not response['success']:
            raise TankError('Unsuccessful tank response: {}'.format(response))
        return response

    def is_load_test_finished(self, load_test_id):
        load_test_status = self.get_load_test_status(load_test_id)
        if load_test_status['status_code'] == 'FINISHED':
            return True, load_test_status
        else:
            return False, load_test_status
