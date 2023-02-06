from aiohttp import web
import pytest

from test_eats_tips_withdrawal import conftest


@pytest.mark.parametrize(
    'jwt, enabled',
    [(conftest.JWT_USER_1, True), (conftest.JWT_USER_4, False)],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 1}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 4}],
    value={'enabled': False},
)
async def test_withdrawal_settings(
        taxi_eats_tips_withdrawal_web,
        mock_eats_tips_partners,
        web_app_client,
        web_context,
        jwt,
        enabled,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    response = await web_app_client.get(
        '/v1/withdrawal/settings', headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'sbp': {'enabled': enabled}}
