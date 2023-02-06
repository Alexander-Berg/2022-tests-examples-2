import pytest


@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
@pytest.mark.parametrize(
    ['yandex_uid', 'expected_code', 'expected_data'],
    (
        pytest.param(
            '1000000000010001',
            200,
            {
                'user': '1609491900:1000010001',
                'password': '9E55mxkmeeCg9ahHWRtEd+dW0PO9YAgDNiGi5dmOe8M=',
                'ttl': 300,
            },
            id='default config',
        ),
        pytest.param(
            '1000000000010002',
            200,
            {
                'user': '1609491901:1000010002',
                'password': 'j83CaufsSu73KxjArJWXNe3+GBGEXyFp5S0lmCvCVbA=',
                'ttl': 301,
            },
            marks=pytest.mark.config(
                CALLCENTER_REG_EPHEMERAL_TTL={'ttl': 301},
            ),
            id='normal config',
        ),
        pytest.param(
            '1000000000010017',
            404,
            {'code': 'not_found', 'message': 'sip_username not found'},
            id='not found',
        ),
    ),
)
async def test_auth_ephemeral(
        taxi_callcenter_reg, yandex_uid, expected_code, expected_data,
):
    await taxi_callcenter_reg.invalidate_caches()
    response = await taxi_callcenter_reg.post(
        '/cc/v1/callcenter-reg/v1/agent/auth/ephemeral',
        headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_data
