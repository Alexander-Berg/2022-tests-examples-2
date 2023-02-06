from typing import Dict
from typing import Optional

import pytest

from test_rida import helpers


TOKEN = helpers.get_auth_token(user_id=2715)
INVALID_TOKEN = TOKEN + 'invalid'


@pytest.mark.parametrize(
    ['headers', 'expected_status', 'expected_response'],
    [
        pytest.param(
            {},
            401,
            {
                'code': 'UNAUTHORIZED',
                'status': 'UNAUTHORIZED',
                'message': 'Missing authorization token',
            },
            id='missing_auth_token',
        ),
        pytest.param(
            {'Authorization': f'Bearer={TOKEN}'},
            403,
            {
                'code': 'INVALID_AUTH',
                'status': 'INVALID_AUTH',
                'message': 'Invalid authorization header',
            },
            id='invalid_auth_header',
        ),
        pytest.param(
            {'Authorization': f'Boober {TOKEN}'},
            403,
            {
                'code': 'INVALID_AUTH',
                'status': 'INVALID_AUTH',
                'message': 'Invalid token scheme',
            },
            id='invalid_token_scheme',
        ),
        pytest.param(
            {'Authorization': f'Bearer {INVALID_TOKEN}'},
            401,
            {
                'code': 'UNAUTHORIZED',
                'status': 'UNAUTHORIZED',
                'message': (
                    'Invalid authorization token, '
                    'Signature verification failed'
                ),
            },
            id='invalid_auth_token',
        ),
        pytest.param(
            {'Authorization': f'Bearer {TOKEN}'},
            401,
            {
                'code': 'UNAUTHORIZED',
                'status': 'UNAUTHORIZED',
                'message': 'No user found',
            },
            id='user_not_found',
        ),
        pytest.param(
            {
                'Authorization': (
                    f'Bearer {helpers.get_auth_token(user_id=1235)}'
                ),
            },
            401,
            {
                'code': 'UNAUTHORIZED',
                'status': 'UNAUTHORIZED',
                'message': 'User device_uuid mismatch',
            },
            id='user_logged_from_another_device',
        ),
    ],
)
async def test_user_auth_errors(
        taxi_rida_web,
        headers: Dict[str, str],
        expected_status: int,
        expected_response: Optional[Dict[str, str]],
):
    response = await taxi_rida_web.get('/ping2', headers=headers)
    assert response.status == expected_status
    if expected_response is not None:
        response_json = await response.json()
        assert response_json == expected_response


async def test_user_auth_success(taxi_rida_web):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.get('/ping2', headers=headers)
    assert response.status == 200
