import pytest

CORPS = [f'corporate_client_identifier_000{i}' for i in range(4)]
CORP_CLIENT_ID, OTHER_CORP_CLIENT_ID = CORPS[1], CORPS[2]

IP_ORIGIN_HEADERS = {'X-Real-Ip': '1.2.3.4', 'Origin': 'testsuite'}

NOT_FOUND = {'code': 'not_found', 'message': 'Not found'}
BAD_RESPONSE = {'code': 'error', 'message': 'Error'}


CARGO_CORP_CASES = (
    'is_b2b_header_set, cargo_corp_code',
    [
        pytest.param(False, 500, id='old way auth, any cargo'),
        pytest.param(True, 200, id='new way auth, cargo 200, not cargo'),
        pytest.param(True, 500, id='new way auth, cargo 500'),
    ],
)
CARGO_CORP_TOKEN_CASES = (
    'cargo_robot_code',
    [pytest.param(404, id='cargo 404'), pytest.param(500, id='cargo 500')],
)

PROXY_401_TEST_URL = '/v1/cargo/proxy_401/cache/test'
DEFAULT_REQUEST = {'x': {'y': 1, 'z': 456}}
