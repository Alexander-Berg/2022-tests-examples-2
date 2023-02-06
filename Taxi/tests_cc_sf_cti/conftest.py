# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import re
import urllib.parse as urlparse

import pytest

from cc_sf_cti_plugins import *  # noqa: F403 F401

from tests_cc_sf_cti import request_container


@pytest.fixture
def _mock_ivr_create_call(mockserver):
    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    def _handler(request):
        request_container.SingleRequestContainer.request = request
        mockserver.make_response(json=dict(), status=200)


@pytest.fixture
def _mock_sf_data_load(mockserver):
    @mockserver.json_handler('/sf-data-load/v1/cc_sf_cti/b2b')
    def _handler(request):
        request_container.SingleRequestContainer.request = request
        mockserver.make_response(json=dict(), status=200)


PHONE2UID_MAP = {'1234': '1234_uid', '100': '100_uid', '42': '42_uid'}
UID2PHONE_MAP = {'1234_uid': '1234', '100_uid': '100', '42_uid': '42'}


@pytest.fixture
def _mock_staff_api(mockserver):
    @mockserver.handler('/staff-production/v3/persons')
    def _handler(request):
        parsed_url = urlparse.urlparse(request.url)
        query = urlparse.parse_qs(parsed_url.query)['_query'][0]
        if query.find('work_phone==') != -1:
            # по добавочному ищем uid
            number = re.search(r'\(work_phone==\d+\)', query).group(0)[13:-1]
            result = []
            if PHONE2UID_MAP.get(number):
                result = [
                    {
                        'work_phone': int(number),
                        'uid': PHONE2UID_MAP[number],
                        'id': 'some_id',
                        'department_group': {
                            'department': {
                                'url': '123',
                                'name': {
                                    'full': {'en': 'yandex', 'ru': 'Яндекс'},
                                    'short': {'en': 'yandex', 'ru': 'Яндекс'},
                                },
                            },
                        },
                    },
                ]
            answer = {'result': result}
            return mockserver.make_response(json=answer, status=200)
        if query.find('uid==') != -1:
            # по uid ищем добавочный
            uid = re.search(r'\(uid=="\w+"\)', query).group(0)[7:-2]
            result = []
            if UID2PHONE_MAP.get(uid):
                result = [
                    {
                        'work_phone': int(UID2PHONE_MAP[uid]),
                        'uid': uid,
                        'id': 'some_id',
                        'department_group': {
                            'department': {
                                'url': '123',
                                'name': {
                                    'full': {'en': 'yandex', 'ru': 'Яндекс'},
                                    'short': {'en': 'yandex', 'ru': 'Яндекс'},
                                },
                            },
                        },
                    },
                ]
            answer = {'result': result}
            return mockserver.make_response(json=answer, status=200)
        return mockserver.make_response(json={}, status=400)
