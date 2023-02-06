import pytest

from eats_catalog import storage


@pytest.mark.now('2021-01-01T09:00:00+03:00')
async def test_without_zone(slug, eats_catalog_storage):
    """
    EDACAT-602: тест проверяет, что при запросе заведения, которое не
    может быть отображено в данных координатах, по слагу, каталог вернет
    информацию о заведении, в которой будет указано, что заведение недоступно
    """

    eats_catalog_storage.add_place(storage.Place())
    eats_catalog_storage.add_zone(storage.Zone())

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 0, 'longitude': 0},
    )

    # Два запроса в стораж - один за данными заведения по слагу, второй -
    # попытка найти доступное заведение того же бренда по переданным
    # координатам
    assert response.status_code == 200

    data = response.json()

    assert data['payload']['foundPlace']['locationParams'] == {
        'deliveryTime': {'max': 70705, 'min': 70695},
        'available': False,
        'availableNow': False,
        'availableByTime': False,
        'availableByLocation': False,
        'distance': 7067.736053440433,
        'availableShippingTypes': [],
        'availableTo': None,
        'availableFrom': None,
        'availableSlug': None,
        'eatDay': None,
        'prepareTime': {'minutes': 0.0, 'readyAt': None},
        'shippingInfoAction': {
            'deliveryFee': {'name': '0 ₽'},
            'message': 'Доставка',
        },
    }

    assert data['payload']['availableTimePicker'] == [[], []]
