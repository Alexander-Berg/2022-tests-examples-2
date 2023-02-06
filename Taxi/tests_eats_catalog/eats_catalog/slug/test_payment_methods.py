from dateutil import parser
import pytest

from eats_catalog import storage


@pytest.mark.now('2021-03-21T13:28:00+00:00')
@pytest.mark.parametrize(
    'country, payment_methods',
    [
        pytest.param(
            storage.Country(country_id=35, name='Россия', code='RU'),
            [1, 2, 3, 4],
            id='RU',
        ),
        pytest.param(
            storage.Country(country_id=5, name='Казахстан', code='KZ'),
            [1, 3, 4],
            id='KZ',
        ),
    ],
)
async def test_kz_payment_methods(
        slug, eats_catalog_storage, country, payment_methods,
):
    """
    EDACAT-713: проверяет, что для заведений работающих в Казахстане
    отображаются правильные методы оплаты
    """

    eats_catalog_storage.add_place(storage.Place(country=country))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-21T10:00:00+00:00'),
                    end=parser.parse('2021-03-21T14:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 0, 'longitude': 0},
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data['payload']['foundPlace']['place']['availablePaymentMethods']
        == payment_methods
    )
