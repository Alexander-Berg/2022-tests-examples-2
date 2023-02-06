from urllib import parse

import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    (
        'updated_from',
        'updated_to',
        'headers',
        'expected_status',
        'expected_json',
    ),
    [
        pytest.param(
            None,
            None,
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok_1.json',
            id='ok active',
        ),
        pytest.param(
            '2021-06-03T01:23:45.678912+0000',
            '2021-06-14T01:23:45.678912+0000',
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok_2.json',
            id='ok from to',
        ),
        pytest.param(
            None,
            None,
            consts.BAD_AUTH_HEADERS,
            403,
            'expected_response_bad_auth_token.json',
            id='bad auth token',
        ),
        pytest.param(
            '2021-06-03T01:23:45.678912+0000',
            None,
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok_3.json',
            id='ok from',
        ),
    ],
)
@consts.mock_tvm_configs()
async def test_post_redirections(
        taxi_vgw_ya_tel_adapter,
        updated_from,
        updated_to,
        headers,
        expected_status,
        expected_json,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
):
    url = '/redirections'
    delim = '?'
    if updated_from:
        url = f'{url}{delim}updated_from={parse.quote(updated_from)}'
        delim = '&'
    if updated_to:
        url = f'{url}{delim}updated_to={parse.quote(updated_to)}'

    response = await taxi_vgw_ya_tel_adapter.get(url, headers=headers)
    assert response.status_code == expected_status
    response_json = response.json()
    if response.status_code == 200:
        response_json = sorted(response_json, key=lambda x: x['id'])
    assert response_json == load_json(expected_json)
