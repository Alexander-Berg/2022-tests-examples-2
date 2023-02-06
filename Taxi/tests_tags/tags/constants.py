from typing import Dict

TAGS_TVM_ID = 20
TAGS_TVM_NAME = 'tags'
TAGS_AUTH = 'OAuth tags-robot-token'
USER_AGENT = 'Taxi-Tags-Uploader'

TEST_LOGIN = 'testlogin'
TEST_TOKEN = 'testtoken'
TEST_LOGIN_HEADER = dict([('X-Yandex-Login', TEST_LOGIN)])
TEST_TOKEN_HEADER = dict([('X-Idempotency-Token', TEST_TOKEN)])

SUPPORTED_ENTITY_TYPES = ['dbid_uuid', 'park', 'park_car_id', 'udid']

_TVM_SERVICES = {'reposition': 18, 'driver-protocol': 19}


def add_tvm_header(load, headers: Dict[str, str], service_name: str):
    if service_name not in _TVM_SERVICES:
        raise Exception('unknown service name')

    tvm_id = _TVM_SERVICES[service_name]
    headers['X-Ya-Service-Ticket'] = load(
        f'tvm2_ticket_{tvm_id}_{TAGS_TVM_ID}',
    )
