import pytest

from taxi_tests.utils import log_requests

PASSPORT_HOST = 'http://blackbox.yandex.net'
DEFAULT_UA = 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv)'


class Session:
    def __init__(self, method='oauth', user_agent=DEFAULT_UA, locale='ru-RU'):
        self.method = method
        self.user_agent = user_agent
        self.yandex_uid = None
        self.token = None
        self.session_id = None
        self.phone = None
        self.locale = locale

    def init(self, phone=None, phones=None, is_staff=None, response_code=None,
             status=None, login=None, scope=None, sleep=None):
        data = {
            'is_staff': is_staff,
            'login': login,
            'method': self.method,
            'phone': phone,
            'phones': phones,
            'response_code': response_code,
            'scope': scope,
            'sesion_id': self.session_id,
            'sleep': sleep,
            'status': status,
            'token': self.token,
            'uid': self.yandex_uid,
        }
        data = {
            key: value
            for key, value in data.items()
            if value is not None
        }
        response = log_requests.post(PASSPORT_HOST + '/control',
                                     json=data).json()
        self.token = response.get('token')
        self.session_id = response.get('session_id')
        self.phone = response.get('phone')
        self.yandex_uid = response.get('uid')


@pytest.fixture
def session_maker():
    return Session
