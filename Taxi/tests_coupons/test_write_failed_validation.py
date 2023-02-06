import datetime

import pytest

from tests_coupons import util


@pytest.mark.parametrize(
    'phone_id, headers, service',
    [pytest.param('5bbb5faf15870bd76635d5e2', {}, None)],
)
@pytest.mark.parametrize(
    'coupon_code, expected_description',
    [('expiredseries', ['Promo code expired on 03/01/2017'])],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
@pytest.mark.parametrize(
    'is_switched_on, codes, services, handlers',
    [
        # Проверка на работу без фильтров
        (True, [], ['taxi'], []),
        # Проверка на то, что фича не работает, если конфигом выключена
        (False, [], ['taxi'], []),
        # Проверка фильтра по коду ошибки
        (True, ['ERROR_TOO_LATE'], ['taxi'], []),
        # Проверка на то,
        # что можно отключить сервис и для него не будет работать фича
        (True, [], [], []),
        # Проверка на фильтрацию по названию хендлера
        (True, [], ['taxi'], ['couponcheck']),
    ],
)
async def test_write_validation_reasons_to_mongodb(
        phone_id,
        headers,
        service,
        coupon_code,
        expected_description,
        is_switched_on,
        codes,
        services,
        handlers,
        taxi_coupons,
        mongodb,
        local_services_card,
        taxi_config,
):
    taxi_config.set_values(
        {
            'COUPONS_EATS_COUPONS_PARAMS': {
                'skip_phone_check_for_support': [],
                'failed_validation_log_settings': {
                    'enabled': is_switched_on,
                    'validation_reason_filters': {
                        'exclude_codes': codes,
                        'include_services': services,
                        'exclude_handlers': handlers,
                    },
                },
            },
        },
    )

    request = util.mock_request_couponcheck(
        coupon_code,
        {'type': 'cash'},
        locale='en',
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )

    assert response.status_code == 200

    doc = mongodb.mdb_promocode_failed_validation_logs.find_one(
        {'promocode': coupon_code},
    )

    # проверяем на примере одного купона,
    # условие - что не фильтранули его запись
    if is_switched_on and not codes and services and not handlers:
        assert doc
        assert doc['promocode'] == coupon_code
        assert doc['yandex_uid'] == '123'
        assert 'validation_context' in doc
        assert 'message' in doc
        assert doc['updated_at'] == datetime.datetime(2017, 3, 13, 8, 30)
        assert doc['validation_code'] == 'ERROR_TOO_LATE'
    else:
        # Если сработал один из фильтров или фича выключена,
        # то мы не найдем документ с промокодом в монге
        assert not doc
