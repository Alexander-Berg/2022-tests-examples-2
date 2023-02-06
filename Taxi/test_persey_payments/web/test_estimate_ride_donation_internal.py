import pytest

from test_persey_payments import conftest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'request_params, expected_resp',
    [
        (
            {
                'order_id': 'order1',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            {
                'amount_info': {
                    'amount': '4.000000',
                    'currency_code': 'RUB',
                    'currency_sign': '₽',
                },
                'is_subscribed': True,
            },
        ),
        (
            {
                'order_id': 'order1',
                'payment_tech_type': 'cash',
                'ride_cost': '6',
            },
            {'is_subscribed': True},
        ),
        (
            {
                'order_id': 'order2',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
        ),
        (
            {
                'order_id': 'order3',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
        ),
        (
            {
                'order_id': 'order3',
                'payment_tech_type': 'card',
                'ride_cost': '10',
            },
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
        ),
        (
            {
                'order_id': 'order4',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            {
                'amount_info': {
                    'amount': '12345.000000',
                    'currency_code': 'RUB',
                    'currency_sign': '₽',
                },
                'is_subscribed': True,
            },
        ),
    ],
)
async def test_simple(taxi_persey_payments_web, request_params, expected_resp):
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/estimate', params=request_params,
    )

    assert response.status == 200
    assert await response.json() == expected_resp


@pytest.mark.pgsql('persey_payments', files=['cache_cleaner.sql'])
@pytest.mark.now('2020-05-02T12:00:00+0')
@conftest.ride_subs_config(
    {
        'order_cache': {
            'cache_ttl_s': 2 * 60,
            'paid_order_ttl_s': 5 * 60,
            'user_ttl_s': 7500,
            'update_batch_size': 20000,
            'delete_batch_size': 20000,
        },
    },
)
@pytest.mark.parametrize(
    'order_id, exp_response_empty',
    [('order1', True), ('order2', False), ('order3', True), ('order4', False)],
)
async def test_cache_cleaner(
        taxi_persey_payments_web, order_id, exp_response_empty,
):
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={
            'order_id': order_id,
            'payment_tech_type': 'card',
            'ride_cost': '6',
        },
    )

    assert response.status == 200
    assert ('amount_info' in await response.json()) ^ exp_response_empty


@pytest.mark.pgsql('persey_payments', files=['market.sql'])
@pytest.mark.parametrize(
    'request_headers, request_params, expected_resp',
    [
        (
            {'X-Yandex-UID': 'market_uid', 'X-Brand': 'market'},
            {
                'order_id': 'order1',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            {
                'amount_info': {
                    'amount': '4.000000',
                    'currency_code': 'RUB',
                    'currency_sign': '₽',
                },
                'is_subscribed': True,
            },
        ),
        (
            {'X-Yandex-UID': 'market_uid', 'X-Brand': 'market'},
            {
                'order_id': 'order1',
                'payment_tech_type': 'card',
                'ride_cost': '6.53',
            },
            {
                'amount_info': {
                    'amount': '3.470000',
                    'currency_code': 'RUB',
                    'currency_sign': '₽',
                },
                'is_subscribed': True,
            },
        ),
    ],
)
async def test_market(
        taxi_persey_payments_web,
        request_headers,
        request_params,
        expected_resp,
):
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/estimate',
        params=request_params,
        headers=request_headers,
    )

    assert response.status == 200
    assert await response.json() == expected_resp


@pytest.mark.pgsql('persey_payments', files=['market.sql'])
@conftest.ride_subs_config({'allowed_brands': ['market']})
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[123])
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
    notify={'a': {'b': 'c'}},
)
async def test_ride_subs_cache(web_app, web_app_client):
    response = await web_app_client.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={'payment_tech_type': 'card', 'ride_cost': '5'},
        headers={'X-Yandex-UID': 'some_uid', 'X-Brand': 'market'},
    )

    assert response.status == 200
    assert await response.json() == {
        'is_subscribed': False,
        'nonzero_donation_if_subscribes': True,
    }

    response = await web_app_client.post(
        '/4.0/persey-payments/v1/web/charity/multibrand/ride_subs',
        json={
            'brands': {'market': {'mod': 123, 'goal': {'fund_id': 'friends'}}},
        },
        headers={'X-Yandex-UID': 'some_uid'},
    )

    assert response.status == 201

    await web_app['context'].ride_subs_cache.refresh_cache()

    response = await web_app_client.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={'payment_tech_type': 'card', 'ride_cost': '5'},
        headers={'X-Yandex-UID': 'some_uid', 'X-Brand': 'market'},
    )

    assert response.status == 200
    assert await response.json() == {
        'is_subscribed': True,
        'amount_info': {
            'amount': '118.000000',
            'currency_code': 'RUB',
            'currency_sign': '₽',
        },
    }

    response = await web_app_client.put(
        '/4.0/persey-payments/v1/web/charity/multibrand/ride_subs',
        json={
            'brands': {'market': {'mod': 10, 'goal': {'fund_id': 'friends'}}},
        },
        headers={'X-Yandex-UID': 'some_uid'},
    )

    assert response.status == 200

    await web_app['context'].ride_subs_cache.refresh_cache()

    response = await web_app_client.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={'payment_tech_type': 'card', 'ride_cost': '5'},
        headers={'X-Yandex-UID': 'some_uid', 'X-Brand': 'market'},
    )

    assert response.status == 200
    assert await response.json() == {
        'is_subscribed': True,
        'amount_info': {
            'amount': '5.000000',
            'currency_code': 'RUB',
            'currency_sign': '₽',
        },
    }

    response = await web_app_client.delete(
        '/4.0/persey-payments/v1/web/charity/multibrand/ride_subs',
        params={'brands': 'market'},
        headers={'X-Yandex-UID': 'some_uid'},
    )

    assert response.status == 204

    await web_app['context'].ride_subs_cache.refresh_cache()

    response = await web_app_client.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={'payment_tech_type': 'card', 'ride_cost': '5'},
        headers={'X-Yandex-UID': 'some_uid', 'X-Brand': 'market'},
    )

    assert response.status == 200
    assert await response.json() == {
        'is_subscribed': False,
        'nonzero_donation_if_subscribes': True,
    }


@pytest.mark.pgsql('persey_payments', files=['market.sql'])
@pytest.mark.parametrize(
    'extra_headers, exp_resp_status',
    [
        pytest.param({}, 200),
        pytest.param({'X-Application': 'IOS'}, 200),
        pytest.param(
            {},
            200,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'market': ['IOS']},
            ),
        ),
        pytest.param(
            {'X-Application': 'IOS'},
            200,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'market': ['IOS']},
            ),
        ),
        pytest.param(
            {'X-Application': 'ANDROID'},
            403,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'market': ['IOS']},
            ),
        ),
        pytest.param(
            {'X-Application': 'IOS'},
            200,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'market': ['IOS:exp3_unsafe'],
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_allow_app',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'market_uid',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'IOS',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'market'},
                    ],
                    value={'allowed': True},
                ),
            ],
        ),
    ],
)
async def test_app_whitelist(
        taxi_persey_payments_web, extra_headers, exp_resp_status,
):
    request_headers = {'X-Yandex-UID': 'market_uid', 'X-Brand': 'market'}
    request_headers.update(extra_headers)

    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/estimate',
        params={
            'order_id': 'order1',
            'payment_tech_type': 'card',
            'ride_cost': '6',
        },
        headers=request_headers,
    )

    assert response.status == exp_resp_status

    if exp_resp_status == 403:
        assert await response.json() == {
            'code': 'ROUNDUPS_DISABLED',
            'message': (
                'Roundups are disabled for brand=market, application=ANDROID'
            ),
        }
