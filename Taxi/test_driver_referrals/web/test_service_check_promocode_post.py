import pytest

from test_driver_referrals import conftest


@pytest.mark.parametrize(
    ('promocode', 'expected_response', 'expected_status'),
    [
        ['НЕ_ПРОМОКОД', {'result': 'Промокод не тот'}, 400],
        [
            'ПРОМОКОД1',
            {'result': 'Промокод ок', 'park_id': 'p1', 'driver_id': 'd1'},
            200,
        ],
    ],
)
@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
async def test_service_check_promocode_post(
        web_app_client, promocode, expected_response, expected_status,
):
    response = await web_app_client.post(
        '/service/check-promocode', json={'promocode': promocode},
    )
    assert response.status == expected_status

    content = await response.json()
    assert content == expected_response
