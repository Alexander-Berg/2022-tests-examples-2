import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.parametrize(
    ('talk_id', 'headers', 'expected_status', 'expected_response'),
    [
        pytest.param(
            '231f7ae3-1d3a-7c9-cc1e-b471ba1142f3',
            consts.AUTH_HEADERS,
            200,
            'call.wav',
            id='ok',
        ),
        pytest.param(
            'nonexistent',
            consts.BAD_AUTH_HEADERS,
            403,
            'expected_response_bad_auth_token.json',
            id='bad auth token',
        ),
        pytest.param(
            'nonexistent',
            consts.AUTH_HEADERS,
            404,
            'expected_response_not_found.json',
            id='not found',
        ),
    ],
)
@consts.mock_tvm_configs()
async def test_get_talks_records(
        taxi_vgw_ya_tel_adapter,
        talk_id,
        headers,
        expected_status,
        expected_response,
        mock_ya_tel,
        load_binary,
        load_json,
):
    response = await taxi_vgw_ya_tel_adapter.get(
        f'/talks/{talk_id}/record/', headers=headers,
    )
    assert response.status_code == expected_status
    if response.status_code == 200:
        assert response.content == load_binary(expected_response)
    else:
        assert response.json() == load_json(expected_response)
