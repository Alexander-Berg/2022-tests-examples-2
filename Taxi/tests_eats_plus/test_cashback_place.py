# pylint: disable=too-many-lines

import pytest

from tests_eats_plus import conftest
DEFAULT_HEADERS = {
    'X-Eats-User': 'user_id=3456726',
    'X-YaTaxi-Pass-Flags': '',
    'x-device-id': 'test_simple',
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_place_happy_path(
        taxi_eats_plus, passport_blackbox, eats_order_stats, plus_wallet,
):
    eats_order_stats()
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': 'first', 'place_id': 1},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback': 15.0,
        'title': 'Вот такой кешбек',
        'description': 'Вот такое описание к кешбеку',
        'icon_url': 'http://first-url.com',
        'plus_details_form': {
            'title': 'Плюс в еде!',
            'description': 'Текст о том какой плюс классный',
            'button': {
                'title': 'Распарсилось хорошо',
                'deeplink': 'eats://fires-deeplink',
            },
            'image_url': 'http://image-url.com',
            'background': {'styles': {'rainbow': True}},
        },
    }


@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.now('2020-11-26T00:00:00.000000')
@pytest.mark.parametrize(
    'user,expected',
    [
        (
            'first',
            {
                'cashback': 15.0,
                'description': 'Вот такое описание к кешбеку',
                'icon_url': 'http://first-url.com',
                'plus_details_form': {
                    'button': {
                        'deeplink': 'eats://fires-deeplink',
                        'title': 'Распарсилось хорошо',
                    },
                    'description': 'Текст о том какой плюс классный',
                    'title': 'Плюс в еде!',
                    'image_url': 'http://image-url.com',
                    'background': {'styles': {'rainbow': True}},
                },
                'title': 'Вот такой кешбек',
            },
        ),
        (
            'other',
            {
                'cashback': 15.0,
                'description': 'Описание к кешбеку',
                'title': 'Смотри какой кешбек',
                'icon_url': 'http://second-url.com',
            },
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_place_experiment_data(
        taxi_eats_plus,
        passport_blackbox,
        user,
        expected,
        plus_wallet,
        eats_order_stats,
):
    eats_order_stats()
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': user, 'place_id': 1},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_place_experiment_not_found(
        taxi_eats_plus, passport_blackbox, eats_order_stats, plus_wallet,
):
    eats_order_stats()
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': 'first', 'place_id': 1},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback': 15.0,
        'title': 'Вот такой кешбек',
        'description': 'Вот такое описание к кешбеку',
        'icon_url': 'http://first-url.com',
        'plus_details_form': {
            'title': 'Плюс в еде!',
            'description': 'Текст о том какой плюс классный',
            'button': {
                'title': 'Распарсилось хорошо',
                'deeplink': 'eats://fires-deeplink',
            },
            'image_url': 'http://image-url.com',
            'background': {'styles': {'rainbow': True}},
        },
    }
