import pytest
from requests import exceptions

from taxi_tests.utils import log_requests

PROTOCOL_HOST = 'http://tc.mobile.yandex.net'
DEFAULT_UA = 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv)'
TIMEOUT = 10
RETRIES = 2


def _json_method(url, *, append_uuid=False, append_date=False):
    def method(self, json, *, session=None, retry_on_500=True):
        headers = {}
        if append_date:
            headers['Date'] = 'Fri, 12 Jul 2019 10:00:00 MSK'
        response = self.post(url, json, append_uuid=append_uuid,
                             session=session, headers=headers,
                             retry_on_500=retry_on_500)
        response.raise_for_status()
        return response.json()
    return method


def _get_method(url, *, append_uuid=False, append_date=False):
    def method(self, params, *, session=None, retry_on_500=True):
        headers = {}
        if append_date:
            headers['Date'] = 'Fri, 12 Jul 2019 10:00:00 MSK'
        response = self.get(url, params, append_uuid=append_uuid,
                            session=session, headers=headers,
                            retry_on_500=retry_on_500)
        response.raise_for_status()
        return response.json()
    return method


class Protocol:
    @staticmethod
    def _method(method, url, *, session, headers, cookies, params,
                append_uuid, retry_on_500=True, retry_on_timeout=True,
                **kwargs):
        headers = {} if headers is None else headers.copy()
        cookies = {} if cookies is None else cookies.copy()
        params = {} if params is None else params.copy()
        if session is not None:
            if session.locale is not None:
                headers['Accept-Language'] = session.locale
            if session.user_agent is not None:
                headers['User-Agent'] = session.user_agent
            if session.token is not None:
                headers['Authorization'] = 'Bearer ' + session.token
            if session.session_id is not None:
                cookies['Session_id'] = session.session_id
            if session.yandex_uid is not None:
                cookies['yandexuid'] = session.yandex_uid
        if cookies:
            headers['Cookie'] = '; '.join(
                key + '=' + value
                for key, value in cookies.items()
            )
        if append_uuid and session and session.yandex_uid is not None:
            params['uuid'] = session.yandex_uid
        for num in range(RETRIES):
            try:
                response = log_requests.request(
                    method, url,
                    headers=headers,
                    timeout=TIMEOUT,
                    params=params,
                    **kwargs,
                )
                if response.status_code != 500 or not retry_on_500:
                    break
            except exceptions.ReadTimeout:
                if not retry_on_timeout or num >= (RETRIES - 1):
                    raise
        return response

    def post(self, path, json, *, session=None, headers=None, cookies=None,
             params=None, append_uuid=None, retry_on_500=True,
             retry_on_timeout=True):
        return self._method(
            'post',
            PROTOCOL_HOST + path,
            json=json,
            session=session,
            headers=headers,
            cookies=cookies,
            params=params,
            append_uuid=append_uuid,
            retry_on_500=retry_on_500,
        )

    def get(self, path, params, *, session=None, headers=None, cookies=None,
            append_uuid=None, retry_on_500=True, retry_on_timeout=True):
        return self._method(
            'get',
            PROTOCOL_HOST + path,
            session=session,
            headers=headers,
            cookies=cookies,
            params=params,
            append_uuid=append_uuid,
            retry_on_500=retry_on_500,
        )

    changeaction = _json_method('/3.0/changeaction')
    changecomment = _json_method('/3.0/changecomment')
    changedestinations = _json_method('/3.0/changedestinations')
    changepayment = _json_method('/3.0/changepayment')
    changeporchnumber = _json_method('/3.0/changeporchnumber')
    changes = _json_method('/3.0/changes')
    email = _json_method('/3.0/email')
    expecteddestinations = _json_method('/3.0/expecteddestinations')
    feedback = _json_method('/3.0/feedback')
    geosearch = _json_method('/3.0/geosearch')
    launch = _json_method('/3.0/launch', append_uuid=True)
    nearestposition = _json_method('/3.0/nearestposition')
    nearestzone = _json_method('/3.0/nearestzone')
    order = _json_method('/3.0/order')
    paymentmethods = _json_method('/3.0/paymentmethods')
    paymentstatuses = _json_method('/3.0/paymentstatuses')
    pickuppoints = _json_method('/3.0/pickuppoints')
    suggest = _json_method('/3.0/suggest', append_date=True)
    pricecat = _json_method('/3.0/pricecat')
    promotions = _json_method('/3.0/promotions')
    reorder = _json_method('/3.0/reorder')
    routestats = _json_method('/3.0/routestats')
    startup = _get_method('/3.0/startup', append_uuid=True)
    suggesteddestinations = _json_method('/3.0/suggesteddestinations')
    suggestedpositions = _json_method('/3.0/suggestedpositions')
    taxiontheway = _json_method('/3.0/taxiontheway')
    taxiroute = _json_method('/3.0/taxiroute')
    translations = _json_method('/3.0/translations')
    updatetips = _json_method('/3.0/updatetips')
    weathersuggest = _json_method('/3.0/weathersuggest')
    zoneinfo = _json_method('/3.0/zoneinfo')


@pytest.fixture
def protocol():
    return Protocol()
