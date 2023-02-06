import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    ('redirection_id', 'headers', 'expected_status', 'expected_json'),
    [
        pytest.param(
            '79a2d7179a4266178b00b817c0c1e6cd00000000',
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok.json',
            id='ok',
        ),
        pytest.param(
            '79a2d7179a4266178b00b817c0c1e6cd00000000',
            consts.BAD_AUTH_HEADERS,
            403,
            'expected_response_bad_auth_token.json',
            id='bad auth token',
        ),
        pytest.param(
            'unknown_redirection',
            consts.AUTH_HEADERS,
            404,
            'expected_response_not_found.json',
            id='not found',
        ),
        pytest.param(
            'a95ffcd10c7215bc9f102535a466848f02000000',
            consts.AUTH_HEADERS,
            410,
            'expected_response_gone.json',
            id='expired',
        ),
    ],
)
@consts.mock_tvm_configs()
async def test_post_redirections(
        taxi_vgw_ya_tel_adapter,
        redirection_id,
        headers,
        expected_status,
        expected_json,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
):
    response = await taxi_vgw_ya_tel_adapter.get(
        f'/redirections/{redirection_id}', headers=headers,
    )
    assert response.status_code == expected_status
    assert response.json() == load_json(expected_json)
