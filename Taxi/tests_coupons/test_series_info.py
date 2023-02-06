async def test_series_info(taxi_coupons):
    expected_series_info = {
        'series_id': 'first',
        'services': ['taxi'],
        'is_unique': True,
        'start': '2016-03-01',
        'finish': '2020-03-01',
        'descr': 'Уникальный, работает',
        'zones': [],
        'creator': 'stromsund',
        'value': 500,
        'is_volatile': False,
        'created': '2016-03-01T03:00:00+0300',
        'external_budget': False,
        'user_limit': 2,
        'currency': 'RUB',
        'creditcard_only': False,
        'country': 'rus',
        'payment_methods': [],
        'percent_limit_per_trip': False,
        'usage_per_promocode': False,
        'first_usage_by_classes': False,
        'first_usage_by_payment_methods': False,
        'for_support': False,
        'classes': ['econom'],
        'count': 3,
        'first_limit': 2,
        'used_count': 2,
    }

    response = await taxi_coupons.post(
        '/internal/series/info', json={'series_id': 'first'},
    )
    assert response.status_code == 200

    assert response.json() == expected_series_info


async def test_series_not_found(taxi_coupons):
    response = await taxi_coupons.post(
        '/internal/series/info', json={'series_id': 'notexists'},
    )
    assert response.status_code == 404
