import pytest

from tests_eats_plus import conftest


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    ['fields_passed_to_eats_discounts'],
    [
        (
            {
                'brand': [122333],
                'place': [1],
                # some orders were from another brand,
                # but the same place, so they got discarded
                # in brand counter
                'brand_orders_count': [10],
                'orders_count': [15],
                'place_orders_count': [15],
            },
        ),
    ],
)
# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'always_get_first_order_and_counters_from_order_stats',
    },
    EATS_PLUS_ORDER_STATS_TIME_THRESHOLD_SETTINGS={
        'time_threshold_sec': 0,
        'counters_subtract_value': 0,
    },
)
async def test_order_stats_counters_are_propagating_in_eats_discounts(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        fields_passed_to_eats_discounts,
):
    """
    Тестируем два аспекта:
    1. Передали в eats-discounts счётчики, полученные из eats-order-stats
    2. Корректно посчитали счетчики по плейсам и брендам

    Переключаем EATS_PLUS_ORDER_STATS_SETTINGS.mode,
    потому что дефолтное поведение - получать только флаг,
    а нам нужны и счётчики тоже.
    """
    eats_order_stats(
        has_orders=True,
        overrided_counters=[
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    # place_id=1 has brand_id=122333
                    {'name': 'brand_id', 'value': '122333'},
                    {'name': 'place_id', 'value': '1'},
                ],
                'value': 10,
            },
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    # will be added to place counter, but not to brand one
                    {'name': 'brand_id', 'value': '123123'},
                    {'name': 'place_id', 'value': '1'},
                ],
                'value': 5,
            },
        ],
    )
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567259',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
            ],
        },
    )

    assert response.status_code == 204

    assert eats_discounts_match.times_called == 1
    discounts_request = (await eats_discounts_match.wait_call())[
        'json_request'
    ].json
    conditions = discounts_request.get('common_conditions', {}).get(
        'conditions', None,
    )
    assert conditions
    assert fields_passed_to_eats_discounts.items() <= conditions.items()


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    ['fields_passed_to_eats_discounts'],
    [
        (
            {
                'brand': [122333],
                'place': [1],
                'brand_orders_count': [7],  # 7 orders from brand 122333
                'orders_count': [
                    12,
                ],  # 7 orders from brand 122333, 5 from 133444
                'place_orders_count': [0],  # 0 orders from place 1,
                # but field place_orders_count must be present
            },
        ),
    ],
)
# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'always_get_first_order_and_counters_from_order_stats',
    },
    EATS_PLUS_ORDER_STATS_TIME_THRESHOLD_SETTINGS={
        'time_threshold_sec': 0,
        'counters_subtract_value': 0,
    },
)
async def test_counters_for_place_present_even_if_user_has_orders_in_eats(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        fields_passed_to_eats_discounts,
):
    """
    Тестируем корнеркейс: пользователь - новичок в ресторане, но не Еде
    (заказал из плейсов 2 и 3, а в тесте ходим для плейса 1).
    Ожидаемое поведение:
    Передаём в eats-discounts счётчик для плейса 1,
    равный нулю (нет заказов в этом плейсе).

    Зачем нужен тест: был баг, когда счётчик не передавался вообще,
    если пользователь уже заказывал в Еде,
    но ещё не заказывал в этом ресторане.
    А должен передаваться, и быть равным нулю.

    Соответственно, тест падал на <=, потому что
    'place_orders_count': [0] - этого в счетчиках для eats-discounts не было.
    А теперь не падает, потому что в счетчики передаем place_orders_count=0.
    """
    eats_order_stats(
        has_orders=True,
        overrided_counters=[
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    # place_id=2 has brand_id=122333
                    {'name': 'brand_id', 'value': '122333'},
                    {'name': 'place_id', 'value': '2'},
                ],
                'value': 7,
            },
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    {'name': 'brand_id', 'value': '133444'},
                    {'name': 'place_id', 'value': '3'},
                ],
                'value': 5,
            },
        ],
    )
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567259',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
            ],
        },
    )

    assert response.status_code == 204

    assert eats_discounts_match.times_called == 1
    discounts_request = (await eats_discounts_match.wait_call())[
        'json_request'
    ].json

    conditions = discounts_request.get('common_conditions', {}).get(
        'conditions', None,
    )
    assert conditions
    assert fields_passed_to_eats_discounts.items() <= conditions.items()


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    ['fields_passed_to_eats_discounts'],
    [
        (
            {
                'brand': [122333],
                'place': [1],
                'brand_orders_count': [123],
                'orders_count': [456],
                'place_orders_count': [345],
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 123,
            'default_place_orders_count': 345,
            'is_first_order': False,
            'orders_count': 456,
        },
        'mode': 'always_get_first_order_and_counters_from_order_stats',
    },
)
async def test_falling_back_to_default_counters(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        fields_passed_to_eats_discounts,
):
    """
    Тестируем fallback на захардкоженые в конфиге счетчики.
    Задаем некорректный ответ eats-order-stats (приходят битые счетчики),
    чтобы вызвать fallback.
    """
    eats_order_stats(
        has_orders=True,
        overrided_counters=[
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    {'name': 'some_inadequate_property', 'value': '122333'},
                    {'name': 'some_inadequate_property_2', 'value': '1'},
                ],
                'value': 10,
            },
        ],
    )
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567259',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
            ],
        },
    )

    assert response.status_code == 204

    assert eats_discounts_match.times_called == 1
    discounts_request = (await eats_discounts_match.wait_call())[
        'json_request'
    ].json
    conditions = discounts_request.get('common_conditions', {}).get(
        'conditions', None,
    )
    assert conditions
    assert fields_passed_to_eats_discounts.items() <= conditions.items()


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    ['fields_passed_to_eats_discounts'],
    [
        (
            {
                'brand': [122333],
                'place': [1],
                'brand_orders_count': [123],
                'orders_count': [456],
                'place_orders_count': [321],
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 123,
            'default_place_orders_count': 345,
            'specific_place_orders_count': {'1': 321},
            'is_first_order': False,
            'orders_count': 456,
        },
        'mode': 'always_get_first_order_and_counters_from_order_stats',
    },
)
async def test_falling_back_to_both_default_and_specific_counters(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        fields_passed_to_eats_discounts,
):
    """
    Тестируем fallback на захардкоженые в конфиге счетчики,
    одновременно дефолтные для бренда и специфичные для плейса.
    Задаем некорректный ответ eats-order-stats (приходят битые счетчики),
    чтобы вызвать fallback.
    """
    eats_order_stats(
        has_orders=True,
        overrided_counters=[
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    {'name': 'some_inadequate_property', 'value': '122333'},
                    {'name': 'some_inadequate_property_2', 'value': '1'},
                ],
                'value': 10,
            },
        ],
    )
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567259',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
            ],
        },
    )

    assert response.status_code == 204

    assert eats_discounts_match.times_called == 1
    discounts_request = (await eats_discounts_match.wait_call())[
        'json_request'
    ].json
    conditions = discounts_request.get('common_conditions', {}).get(
        'conditions', None,
    )
    assert conditions
    assert fields_passed_to_eats_discounts.items() <= conditions.items()
