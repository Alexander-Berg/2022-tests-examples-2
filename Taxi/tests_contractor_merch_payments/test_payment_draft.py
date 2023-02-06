import pytest

from tests_contractor_merch_payments import utils

REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT = {
    'id_in_set': ['park_id_contractor_id'],
    'projection': ['data.balance_limit'],
}


async def payment_draft_request(
        client, request_type, park_id, contractor_id, idempotency_token,
):
    if request_type == 'driver':
        url = '/driver/v1/contractor-merch-payments/payment/draft'

        headers = utils.get_headers(park_id, contractor_id, idempotency_token)
        body = None
    elif request_type == 'internal':
        url = '/internal/v1/payment/draft'

        headers = {
            'X-Idempotency-Token': idempotency_token,
            'Accept-Language': 'en_GB',
        }

        body = {
            'park_id': park_id,
            'contractor_id': contractor_id,
            'driver_application': 'Taximeter 9.90',
        }
    else:
        raise RuntimeError(f'Unknown request type {request_type}')

    return await client.post(url, headers=headers, json=body)


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    'park_id, contractor_id, idempotency_token',
    [
        pytest.param(
            'park-id-100',
            'contractor-id-100',
            'payment_idempotency-token-100',
        ),
    ],
)
async def test_payment_draft_inserting(
        taxi_contractor_merch_payments,
        pgsql,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        request_type,
        park_id,
        contractor_id,
        idempotency_token,
):
    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id=park_id,
        contractor_id=contractor_id,
        idempotency_token=idempotency_token,
    )

    assert response.status == 200

    payments = utils.get_payments_by_token(pgsql, idempotency_token)
    assert len(payments) == 1

    payment_id = payments[0][0]
    assert payment_id.startswith('YANDEXPRO-')

    assert response.json() == {
        'payment_id': payment_id,
        'qr_code': utils.DEEP_LINK_PROXY.format(payment_id),
        'ttl_sec': 300,
    }

    assert payments[0] == (
        payment_id,
        idempotency_token,
        park_id,
        contractor_id,
        None,
        None,
        'draft',
    )

    assert mock_fleet_transactions_api.balances_list.times_called == 1
    balances_request = mock_fleet_transactions_api.balances_list.next_call()[
        'request'
    ]
    balances_request.json['query']['balance'].pop('accrued_ats')
    assert balances_request.json == {
        'query': {
            'balance': {},
            'park': {
                'driver_profile': {'ids': ['contractor-id-100']},
                'id': 'park-id-100',
            },
        },
    }

    assert mock_parks_activation.handler.times_called == 1
    assert mock_parks_activation.handler.next_call()['request'].json == {
        'ids_in_set': ['clid1'],
    }

    assert mock_fleet_parks.park_list.times_called == 1
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park-id-100']}},
    }


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    'park_id, contractor_id, idempotency_token',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-other',
            'payment_idempotency-token-1',
            id='test contractor changed',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-draft-and-success',
            'payment_idempotency-token-3',
            id='in succes state',
            marks=[
                pytest.mark.now('2021-07-01T14:00:06'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=10,
                ),
            ],
        ),
    ],
)
async def test_incorrect_retry(
        taxi_contractor_merch_payments,
        load_json,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        request_type,
        park_id,
        contractor_id,
        idempotency_token,
):
    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id=park_id,
        contractor_id=contractor_id,
        idempotency_token=idempotency_token,
    )

    assert response.status == 400

    error_response = load_json('error_response.json')
    error_response['message'] = error_response['message'].format(
        idempotency_token,
    )

    assert response.json() == error_response


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    'park_id, contractor_id, idempotency_token, payment_id',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-draft-and-success',
            'payment_idempotency-token-1',
            'payment_id-1',
        ),
    ],
)
async def test_driver_payment_draft_retry(
        taxi_contractor_merch_payments,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        request_type,
        park_id,
        contractor_id,
        idempotency_token,
        payment_id,
):
    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id=park_id,
        contractor_id=contractor_id,
        idempotency_token=idempotency_token,
    )

    assert response.status == 200

    assert response.json() == {
        'payment_id': payment_id,
        'qr_code': utils.DEEP_LINK_PROXY.format(payment_id),
        'ttl_sec': 300,
    }


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.pgsql('contractor_merch_payments', files=[])
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.parametrize(
    [
        'balance',
        'balance_limit',
        'can_cash',
        'park_fields_update',
        'expected_problem_description',
    ],
    [
        pytest.param(
            '0',
            '0',
            None,
            None,
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            id='not_enough_money_on_drivers_balance with balance_limit = 0',
        ),
        pytest.param(
            '1',
            '1',
            None,
            None,
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            id='not_enough_money_on_drivers_balance with balance_limit > 0',
        ),
        pytest.param(
            '0',
            '-1',
            None,
            None,
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            id='not_enough_money_on_drivers_balance with balance_limit < 0',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            {
                'code': 'park_has_not_enough_money',
                'localized_message': 'park_has_not_enough_money-tr',
            },
            id='park_has_not_enough_money enabled check',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            None,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=False,
            ),
            id='park_has_not_enough_money disabled check',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            None,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_1.json',
                ),
            ],
            id='found in no_cash_check_park_ids',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            {
                'code': 'park_has_not_enough_money',
                'localized_message': 'park_has_not_enough_money-tr',
            },
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_2.json',
                ),
            ],
            id='not_found in no_cash_check_park_ids',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            None,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_3.json',
                ),
            ],
            id='found in secret shoppers',
        ),
        pytest.param(
            None,
            None,
            None,
            {'is_billing_enabled': False},
            {
                'code': 'billing_is_disabled_for_park',
                'localized_message': 'billing_is_disabled_for_park-tr',
            },
            id='billing_is_disabled_for_park',
        ),
        pytest.param(
            None,
            None,
            None,
            {'country_id': 'ukr'},
            {
                'code': 'unsupported_country',
                'localized_message': 'unsupported_country-tr',
            },
            id='unsupported_country',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            {
                'code': 'balance_payments_is_disabled_for_park',
                'localized_message': (
                    'balance_payments_is_disabled_for_park-tr'
                ),
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_DISABLED_PARK_IDS=['park_id'],
            ),
            id='balance_payments_is_disabled_for_park',
        ),
    ],
)
async def test_cannot_buy(
        taxi_contractor_merch_payments,
        taxi_contractor_merch_payments_monitor,
        load_json,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mockserver,
        request_type,
        balance,
        can_cash,
        park_fields_update,
        expected_problem_description,
        balance_limit,
):
    mock_driver_profiles.balance_limit = balance_limit
    before = await taxi_contractor_merch_payments_monitor.get_metric(
        'cannot-make-draft-reason',
    )
    if balance:
        mock_fleet_transactions_api.balance = balance
    if can_cash is not None:
        mock_parks_activation.can_cash = can_cash
    if park_fields_update:
        mock_fleet_parks.fields_update = park_fields_update

    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id='park_id',
        contractor_id='contractor_id',
        idempotency_token='idempotency_token',
    )

    after = await taxi_contractor_merch_payments_monitor.get_metric(
        'cannot-make-draft-reason',
    )
    if balance_limit:
        assert mock_driver_profiles.driver_profiles.times_called == 1
        assert (
            mock_driver_profiles.driver_profiles.next_call()['request'].json
            == REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT
        )

    if expected_problem_description:
        assert response.status == 400
        assert response.json() == {
            'code': 'cannot_buy',
            'message': expected_problem_description['code'],
            'problem_description': expected_problem_description,
        }
        assert (
            after.get(expected_problem_description['code'])
            - before.get(expected_problem_description['code'], 0)
            == 1
        )
    else:
        assert response.status == 200


REQUEST_TO_FLEET_ANTIFRAUD = {
    'park_id': 'park_id',
    'contractor_id': 'contractor_id',
    'do_update': 'false',
}


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.pgsql('contractor_merch_payments', files=[])
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.parametrize(
    'balance, fleet_antifraud_limit,' 'expected_problem_description',
    [
        pytest.param(
            '0',
            '0',
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not_enough_money_on_drivers_balance'
            ' with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '0',
            '0',
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '1',
            '1',
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit > 0',
        ),
        pytest.param(
            '1',
            '1',
            None,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='ok with fleet_antifraud_limit disabled',
        ),
        pytest.param(
            '0',
            '-1',
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit < 0',
        ),
        pytest.param(
            '0',
            '-1',
            {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit < 0',
        ),
    ],
)
async def test_cannot_buy_fleet_antifraud(
        taxi_config,
        taxi_contractor_merch_payments,
        load_json,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mockserver,
        request_type,
        balance,
        expected_problem_description,
        fleet_antifraud_limit,
):
    mock_fleet_antifraud.fleet_antifraud_limit = fleet_antifraud_limit

    mock_fleet_transactions_api.balance = balance

    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id='park_id',
        contractor_id='contractor_id',
        idempotency_token='idempotency_token',
    )

    if (
            taxi_config.get('CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK')
            is not None
            and taxi_config.get(
                'CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK',
            )
    ):
        assert mock_fleet_antifraud.fleet_antifraud.times_called == 1

        request_query_fleet_antifraud = dict(
            mock_fleet_antifraud.fleet_antifraud.next_call()['request'].query,
        )
        assert request_query_fleet_antifraud == REQUEST_TO_FLEET_ANTIFRAUD

    if expected_problem_description:
        assert response.status == 400
        assert response.json() == {
            'code': 'cannot_buy',
            'message': expected_problem_description['code'],
            'problem_description': expected_problem_description,
        }
    else:
        assert response.status == 200


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=10)
@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    'park_id, contractor_id, expect_ok',
    [
        pytest.param(
            'park-id-1',
            'contractor-some-new-driver',
            True,
            id='everything ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-draft-and-success',
            False,
            marks=pytest.mark.now('2021-07-01T14:00:06'),
            id='recent success is not ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-draft-and-success',
            True,
            marks=pytest.mark.now('2021-07-01T14:00:11'),
            id='recent draft is ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-target_success',
            False,
            marks=pytest.mark.now('2022-07-01T14:00:06'),
            id='target_success is not ok always',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-contractor_declined',
            True,
            marks=pytest.mark.now('2021-07-01T14:00:11'),
            id='contractor_declined is ok',
        ),
    ],
)
async def test_pending_payments(
        taxi_contractor_merch_payments,
        load_json,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        request_type,
        park_id,
        contractor_id,
        expect_ok,
):
    response = await payment_draft_request(
        client=taxi_contractor_merch_payments,
        request_type=request_type,
        park_id=park_id,
        contractor_id=contractor_id,
        idempotency_token='new-idempotency_token',
    )

    if expect_ok:
        assert response.status == 200
    else:
        assert response.status == 400
        assert response.json() == {
            'code': 'cannot_buy',
            'message': 'contractor_has_pending_payments',
            'problem_description': {
                'code': 'contractor_has_pending_payments',
                'localized_message': 'contractor_has_pending_payments-tr',
            },
        }
