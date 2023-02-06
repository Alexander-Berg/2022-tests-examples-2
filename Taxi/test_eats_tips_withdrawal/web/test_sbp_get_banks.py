import pytest


@pytest.mark.parametrize(
    'short_list, expected_result',
    [
        (
            True,
            {
                'banks': [
                    {
                        'id': '100000000001',
                        'title': 'Газпромбанк',
                        'image': 'http://bank.image.ru',
                    },
                ],
            },
        ),
        (
            False,
            {
                'banks': [
                    {
                        'id': '100000000001',
                        'title': 'Газпромбанк',
                        'image': 'http://bank.image.ru',
                    },
                    {'id': '100000000002', 'title': 'РНКО Платежный центр'},
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_sbp_get_banks(
        taxi_eats_tips_withdrawal_web, short_list, expected_result,
):
    response = await taxi_eats_tips_withdrawal_web.get(
        '/v1/sbp/get-banks', params={'short_list': short_list},
    )
    content = await response.json()
    assert content == expected_result
