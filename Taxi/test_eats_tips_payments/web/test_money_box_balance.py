from aiohttp import web
import pytest


@pytest.mark.parametrize(
    ('box_id', 'expected_status', 'expected_response'),
    (
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            200,
            {'balance': '42'},
            id='success',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000002', 404, None, id='closed',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000003', 404, None, id='not-found',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_money_box_transfer(
        web_app_client,
        mock_best2pay,
        load,
        box_id,
        expected_status,
        expected_response,
):
    @mock_best2pay('/webapi/b2puser/sd-services/SDGetBalance')
    async def _mock_b2p_payout(request):
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load('b2p_sd_balance_response.xml'),
        )

    response = await web_app_client.get(
        '/internal/v1/money-box/balance', params={'box_id': box_id},
    )
    assert response.status == expected_status
    if expected_response:
        response_json = await response.json()
        assert response_json == expected_response
