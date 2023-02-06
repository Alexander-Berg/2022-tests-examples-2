import datetime

from aiohttp import web
import pytest

NOW = datetime.datetime(2021, 12, 7, 14, 30, 15, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    ('box_id', 'expected_status', 'payments_status', 'expected_response'),
    (
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            200,
            200,
            {
                'id': '20000000-0000-0000-0000-000000000200',
                'place_id': '10000000-0000-0000-0000-000000000100',
                'brand_slug': 'shoko',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000001',
                'display_name': 'копилка 1',
                'alias': '0002000',
                'balance': '42.0',
                'registration_date': '2021-10-30T17:00:00+03:00',
                'trans_guest': True,
                'trans_guest_block': True,
            },
            id='normal',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            200,
            404,
            {
                'id': '20000000-0000-0000-0000-000000000200',
                'place_id': '10000000-0000-0000-0000-000000000100',
                'brand_slug': 'shoko',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000001',
                'display_name': 'копилка 1',
                'alias': '0002000',
                'balance': '0.0',
                'registration_date': '2021-10-30T17:00:00+03:00',
                'trans_guest': True,
                'trans_guest_block': True,
            },
            id='normal-404',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000777',
            404,
            200,
            {},
            id='not-found',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000202', 404, 200, {}, id='deleted',
        ),
        pytest.param('bad', 400, 200, {}, id='bad-box'),
    ),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_tips_partners', files=['pg_money_box.sql'])
async def test_money_box_get(
        taxi_eats_tips_partners_web,
        mock_eats_tips_payments,
        web_context,
        box_id,
        expected_status,
        payments_status,
        expected_response,
):
    @mock_eats_tips_payments('/internal/v1/money-box/balance')
    async def _mock_alias_to_id(request):
        return web.json_response({'balance': '42.0'}, status=payments_status)

    response = await taxi_eats_tips_partners_web.get(
        '/v1/money-box', params={'id': box_id},
    )
    assert response.status == expected_status
    if expected_response:
        content = await response.json()
        assert content == expected_response
