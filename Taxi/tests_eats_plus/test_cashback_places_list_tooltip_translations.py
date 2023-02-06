import pytest

from tests_eats_plus import conftest

TOOLTIP_DESCRIPTION = (
    'Заказывая здесь, вы получаете кешбэк баллами с каждого заказа. '
    'Баллы можно тратить на поездки в '
    'такси, покупки, кино и многое другое. 1 балл = 1 рубль'
)

TOOLTIP_TITLE = 'Еда с Плюсом выгоднее'


TRANSLATIONS = {
    'eats-plus': {
        'eats-plus_places-list_tooltip_description': {
            'ru': TOOLTIP_DESCRIPTION,
        },
        'eats-plus_places-list_tooltip_title': {'ru': TOOLTIP_TITLE},
    },
}


def tooltip_by_platform():
    return {'description': TOOLTIP_DESCRIPTION, 'title': TOOLTIP_TITLE}


PLATFORMS_FOR_TOOLTIPS = ['desktop_web']


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.experiments3(filename='exp3_eats_plus_tooltip_settings.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    'platform',
    (
        'desktop_web',
        'superapp_taxi_web',
        'ios_app',
        'superapp_taxi_web',
        'android_app',
    ),
)
async def test_eats_plus_tooltip(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        platform,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        # 5 - active=false
        # 6 - all cashback isn't active
        # 404 - doesn't exist
        headers={'x-platform': platform},
        json={'yandex_uid': 'user-uid', 'place_ids': [1, 2, 3, 4, 5, 6]},
    )

    assert response.status_code == 200
    response = response.json()

    if platform in PLATFORMS_FOR_TOOLTIPS:
        for cashbacks in response['cashback']:
            assert cashbacks['tooltip'] == tooltip_by_platform()
    else:
        for cashbacks in response['cashback']:
            assert 'tooltip' not in cashbacks
