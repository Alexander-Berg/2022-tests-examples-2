import datetime

import pytest

NOW = datetime.datetime(2021, 12, 7, 14, 30, 15, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    ('places', 'expected_status', 'expected_response'),
    (
        pytest.param(
            '10000000-0000-0000-0000-000000000100',
            200,
            {
                'boxes': [
                    {
                        'id': '20000000-0000-0000-0000-000000000200',
                        'place_id': '10000000-0000-0000-0000-000000000100',
                        'brand_slug': 'shoko',
                        'fallback_partner_id': (
                            '00000000-0000-0000-0000-000000000001'
                        ),
                        'display_name': 'копилка 1',
                        'alias': '0002000',
                        'registration_date': '2021-10-30T17:00:00+03:00',
                        'trans_guest': True,
                        'trans_guest_block': True,
                    },
                    {
                        'id': '20000000-0000-0000-0000-000000000201',
                        'place_id': '10000000-0000-0000-0000-000000000100',
                        'brand_slug': 'shoko',
                        'fallback_partner_id': (
                            '00000000-0000-0000-0000-000000000001'
                        ),
                        'display_name': 'копилка 2',
                        'alias': '0002010',
                        'registration_date': '2021-10-30T17:00:00+03:00',
                        'trans_guest': True,
                        'trans_guest_block': True,
                    },
                ],
            },
            id='normal',
        ),
        pytest.param(
            '10000000-0000-0000-0000-000000000103', 404, {}, id='deleted',
        ),
        pytest.param(
            '10000000-0000-0000-0000-000000000777', 404, {}, id='not found',
        ),
        pytest.param('bad', 400, {}, id='bad-box'),
    ),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_tips_partners', files=['pg_money_box.sql'])
async def test_money_box_list_get(
        taxi_eats_tips_partners_web,
        web_context,
        places,
        expected_status,
        expected_response,
):
    response = await taxi_eats_tips_partners_web.get(
        '/v1/money-box/list', params={'places_ids': places},
    )
    assert response.status == expected_status
    if expected_response:
        content = await response.json()
        assert content == expected_response
