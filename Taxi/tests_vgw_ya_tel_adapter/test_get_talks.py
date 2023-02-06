import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.parametrize(
    ['headers', 'expected_status'],
    [(consts.AUTH_HEADERS, 200), (consts.BAD_AUTH_HEADERS, 403)],
)
@pytest.mark.parametrize(
    'url',
    [
        '/talks?start_from=2013-04-01T14:00:00%2B0400'
        '&start_to=2013-04-01T15:00:00%2B0400',
        '/redirections/79a2d7179a4266178b00b817c0c1e6cd00000000/talks',
    ],
)
@consts.mock_tvm_configs()
async def test_get_talks(
        taxi_vgw_ya_tel_adapter, url, headers, expected_status, load_json,
):
    response = await taxi_vgw_ya_tel_adapter.get(url, headers=headers)
    assert response.status_code == expected_status
    if response.status_code == 200:
        assert response.json() == []
    elif response.status_code == 403:
        assert response.json() == load_json(
            'expected_response_bad_auth_token.json',
        )
