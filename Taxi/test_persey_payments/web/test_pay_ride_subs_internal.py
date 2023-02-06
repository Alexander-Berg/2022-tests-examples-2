import pytest


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'expected_donations',
        'invoice_started',
        'expected_resp',
        'expected_resp_code',
    ],
    [
        (
            [
                (
                    'friends',
                    'market_uid',
                    '3',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'market',
                    'order777',
                    'started',
                ),
            ],
            1,
            {},
            200,
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        load_json,
        get_ride_subs,
        get_ride_subs_cache,
        get_donations,
        mock_invoice_create,
        mock_invoice_update,
        mock_zalogin,
        expected_donations,
        invoice_started,
        expected_resp,
        expected_resp_code,
):
    zalogin_mock = mock_zalogin('market_uid', 'zalogin_resp.json')
    invoice_create_mock = mock_invoice_create(
        'expected_invoice_create_request.json',
    )
    invoice_update_mock = mock_invoice_update(
        'expected_invoice_update_request.json',
    )

    response = await taxi_persey_payments_web.post(
        '/internal/v1/charity/ride_subs/pay',
        json={
            'order_id': 'order777',
            'ride_cost': {'amount': 777, 'currency_code': 'RUB'},
            'payment_tech': {
                'payment_method_id': 'card-x777',
                'payment_type': 'card',
            },
        },
        headers={
            'X-Yandex-UID': 'market_uid',
            'X-Remote-IP': '127.0.0.1',
            'X-Brand': 'market',
        },
    )

    assert response.status == expected_resp_code, await response.json()
    assert await response.json() == expected_resp

    assert invoice_create_mock.times_called == invoice_started
    assert invoice_update_mock.times_called == invoice_started
    assert zalogin_mock.times_called == 1
    assert get_donations() == expected_donations


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'extra_headers, exp_resp_status',
    [
        pytest.param({}, 200),
        pytest.param({'X-Application': 'IOS'}, 200),
        pytest.param(
            {},
            403,
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
        pytest.param(
            {'X-Application': 'IOS'},
            403,
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
                    value={},
                ),
            ],
        ),
    ],
)
async def test_app_whitelist(
        taxi_persey_payments_web,
        mock_zalogin,
        mock_invoice_create,
        mock_invoice_update,
        extra_headers,
        exp_resp_status,
):
    request_headers = {
        'X-Yandex-UID': 'market_uid',
        'X-Remote-IP': '127.0.0.1',
        'X-Brand': 'market',
    }
    request_headers.update(extra_headers)

    mock_zalogin('market_uid', 'zalogin_resp.json')
    mock_invoice_create('expected_invoice_create_request.json')
    mock_invoice_update('expected_invoice_update_request.json')

    response = await taxi_persey_payments_web.post(
        '/internal/v1/charity/ride_subs/pay',
        json={
            'order_id': 'order777',
            'ride_cost': {'amount': '777', 'currency_code': 'RUB'},
            'payment_tech': {
                'payment_method_id': 'card-x777',
                'payment_type': 'card',
            },
        },
        headers=request_headers,
    )

    assert response.status == exp_resp_status

    request_app = extra_headers.get('X-Application')

    if exp_resp_status == 403:
        assert await response.json() == {
            'code': 'ROUNDUPS_DISABLED',
            'message': (
                'Roundups are disabled for brand=market, '
                f'application={request_app}'
            ),
        }
