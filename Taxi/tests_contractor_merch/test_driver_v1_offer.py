# pylint: disable=too-many-lines

import copy

import aiohttp
import pytest

from tests_contractor_merch import util

HEADERS = util.get_headers('park_id', 'driver_id')

MUTABLE = 'by-offer-id'
IMMUTABLE = 'by-immutable-id'
FETCH_BY_IDS = {
    MUTABLE: '/feeds/v1/fetch_by_id',
    IMMUTABLE: '/feeds/v1/fetch_by_package_id',
}
HANDLERS_BY_IDS = {
    MUTABLE: '/driver/v1/contractor-merch/v1/offer/feed-id-1',
    IMMUTABLE: (
        '/driver/v1/contractor-merch/v1/'
        'offer-by-immutable-id/feeds-admin-id-1'
    ),
}

FEEDS_RESPONSE_JSON = 'responses/feeds_response.json'

TRANSLATIONS = {
    'list_v1.title': {'en': 'Title'},
    'list_v1.subtitle': {'en': 'Subtitle'},
    'category.tire': {'en': 'Tires and so'},
    'category.washing': {'en': 'Washing and so'},
    'category.washing.slider': {'en': 'WASH-WASH-WASH'},
    **util.ERROR_TRANSLATIONS,
}
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_ok(
        taxi_contractor_merch,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_driver_tags,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        load_json,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        assert request.json['channels'] == [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'experiment:contractor_merch_offer_matched',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ]

        if offer_id_type == MUTABLE:
            assert request.json['feed_id'] == 'feed-id-1'
        else:
            assert request.json['package_ids'] == ['feeds-admin-id-1']

        return load_json(FEEDS_RESPONSE_JSON)

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200
    content = response.json()
    assert content == util.get_expected_offer_response(load_json)


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_no_checks_if_balance_payment_disabled(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        response = load_json(FEEDS_RESPONSE_JSON)
        response['feed'][0]['payload']['balance_payment'] = False
        return response

    mock_fleet_transactions_api.balance = '-200'

    assert mock_driver_profiles.driver_profiles.times_called == 0

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200


# Check if config3.0 value is disabled
# and config to enable park check
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_park_can_buy_disabled(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    mock_driver_tags.tags = ['loyka_available']

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert mock_parks_activation.handler_balances.times_called == 0
    assert mock_parks_activation.handler_retrieve.times_called == 0

    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)

    assert response.json() == expected_offer_response


# Check if config value is park_balance_check
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    (
        'balance',
        'threshold',
        'threshold_dynamic',
        'park_can_buy',
        'contract_balance_service_id',
    ),
    [
        pytest.param('200', '0', '0', True, 111),
        pytest.param('0', '200', '0', True, 111),
        pytest.param('0', '400', '200', True, 111),
        pytest.param('0', '0', '0', False, 111),
        pytest.param('200', '0', '0', False, 112),
    ],
)
async def test_park_can_buy_park_balance_check(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        balance,
        threshold,
        threshold_dynamic,
        park_can_buy,
        contract_balance_service_id,
):
    mock_fleet_parks.updates = {'driver_partner_source': 'selfemployed_fns'}

    mock_parks_activation.balance = balance
    mock_parks_activation.threshold = threshold
    mock_parks_activation.threshold_dynamic = threshold_dynamic
    mock_parks_activation.service_id = contract_balance_service_id

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert mock_parks_activation.handler_balances.times_called == 1
    assert mock_parks_activation.handler_retrieve.times_called == 0

    call_args = mock_parks_activation.handler_balances.next_call()[
        'request'
    ].args
    assert call_args['park_id'] == 'clid1'

    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)

    if not park_can_buy:
        expected_offer_response = {
            **expected_offer_response,
            'is_avaliable': False,
            'is_available': False,
            'problem_description': {
                'code': 'park_has_not_enough_money',
                'localized_message': 'park_has_not_enough_money-tr',
            },
        }

    assert response.json() == expected_offer_response


# Check if config value is cash_check
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize('park_can_cash', [True, False])
async def test_park_can_buy_cash_check(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        park_can_cash,
):
    headers = {
        **HEADERS,
        'X-YaTaxi-Driver-Profile-Id': 'a1d9721eefb94befa705fa0d86b58efb',
    }

    mock_parks_activation.can_cash = park_can_cash

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=headers,
    )

    assert mock_parks_activation.handler_balances.times_called == 0
    assert mock_parks_activation.handler_retrieve.times_called == 1

    call_args = mock_parks_activation.handler_retrieve.next_call()[
        'request'
    ].json
    assert call_args == {'ids_in_set': ['clid1']}

    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)

    if not park_can_cash:
        expected_offer_response = {
            **expected_offer_response,
            'is_avaliable': False,
            'is_available': False,
            'problem_description': {
                'code': 'park_has_not_enough_money',
                'localized_message': 'park_has_not_enough_money-tr',
            },
        }

    assert response.json() == expected_offer_response


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    'driver_id, meta_info, expected_problem_description',
    [
        pytest.param(
            'one_offer_total_limit_excceded',
            {'total_per_driver_limit': 1},
            {
                'code': 'one_offer_total_limit_excceded',
                'localized_message': 'one_offer_total_limit_excceded-tr',
            },
            id='total_limit_excceded',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'total_per_driver_limit': 2},
            None,
            id='total_limit_unreached',
        ),
        pytest.param(
            'one_offer_total_limit_excceded', {}, None, id='total_limit_unset',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 1},
            {
                'code': 'one_offer_daily_limit_excceded',
                'localized_message': 'one_offer_daily_limit_excceded-tr',
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_excceded',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 2},
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_unreached',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 1},
            None,
            marks=[pytest.mark.now('2021-07-02T15:00:00Z')],
            id='daily_limit_last_purchases_long_time_ago',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {},
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_unset',
        ),
        pytest.param(
            'driver_has_pending_purchases',
            {},
            {
                'code': 'driver_has_pending_purchases',
                'localized_message': 'driver_has_pending_purchases-tr',
            },
        ),
        pytest.param(
            'purchase_period',
            {},
            {
                'code': 'driver_has_pending_purchases',
                'localized_message': 'driver_has_pending_purchases-tr',
            },
            marks=[
                pytest.mark.now('2021-07-01T14:00:20Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=15,
                ),
            ],
            id='purchase_period triggers',
        ),
        pytest.param(
            'purchase_period',
            {},
            None,
            marks=[
                pytest.mark.now('2021-07-01T14:00:30Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=15,
                ),
            ],
            id='purchase_period does not trigger 1',
        ),
        pytest.param(
            'purchase_period',
            {},
            None,
            marks=[
                pytest.mark.now('2021-07-01T14:00:10Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=0,
                ),
            ],
            id='purchase_period does not trigger 2',
        ),
    ],
)
async def test_driver_limits(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        driver_id,
        meta_info,
        expected_problem_description,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        response = load_json(FEEDS_RESPONSE_JSON)
        response['feed'][0]['payload']['meta_info'].update(meta_info)
        return response

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': driver_id},
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)
    if expected_problem_description:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': False,
            'is_avaliable': False,
            'problem_description': expected_problem_description,
        }
    else:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': True,
            'is_avaliable': True,
        }

    assert response.json() == expected_offer_response


RESPONSE_FROM_DRIVER_PROFILES_BALANCE_LIMIT = {
    'profiles': [
        {
            'data': {'balance_limit': '0'},
            'park_driver_profile_id': 'change this id in mock',
        },
    ],
}


@pytest.mark.now('2021-07-01T14:00:00Z')
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    ['total_balance', 'balance_limit'],
    [
        pytest.param(
            '199', '0', id='not enough total_balance with balance_limit = 0',
        ),
        pytest.param('200', '1', id='not enough with balance_limit > 0'),
        pytest.param('199', '-1', id='not enough with balance_limit < 0'),
    ],
)
async def test_balance(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        total_balance,
        balance_limit,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles(request):
        resp = copy.deepcopy(RESPONSE_FROM_DRIVER_PROFILES_BALANCE_LIMIT)
        resp['profiles'][0]['data']['balance_limit'] = balance_limit
        resp['profiles'][0]['park_driver_profile_id'] = request.json[
            'id_in_set'
        ][0]
        return resp

    mock_fleet_transactions_api.balance = total_balance
    mock_driver_profiles.driver_profiles = _driver_profiles

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert response.status == 200
    assert response.json() == {
        **util.get_expected_offer_response(load_json),
        'is_avaliable': False,
        'is_available': False,
        'problem_description': {
            'code': 'not_enough_money_on_drivers_balance',
            'localized_message': 'not_enough_money_on_drivers_balance-tr',
        },
    }
    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert mock_fleet_transactions_api.balances_list.times_called == 1
    assert (
        mock_fleet_transactions_api.balances_list.next_call()['request'].json
        == {
            'query': {
                'balance': {'accrued_ats': ['2021-07-01T14:00:00+00:00']},
                'park': {
                    'driver_profile': {'ids': ['some_driver']},
                    'id': 'park_id',
                },
            },
        }
    )


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_no_promocodes_left(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1

    assert response.status == 200
    assert response.json() == {
        **util.get_expected_offer_response(load_json),
        'is_available': False,
        'is_avaliable': False,
        'problem_description': {
            'code': 'no_promocodes_left',
            'localized_message': 'no_promocodes_left-tr',
        },
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_billing_is_disabled_for_park(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    mock_fleet_parks.is_billing_enabled = False

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1

    assert response.status == 200
    assert response.json() == {
        **util.get_expected_offer_response(load_json),
        'is_available': False,
        'is_avaliable': False,
        'problem_description': {
            'code': 'billing_is_disabled_for_park',
            'localized_message': 'billing_is_disabled_for_park-tr',
        },
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.config(
    CONTRACTOR_MERCH_DISABLED_PARK_IDS=['park1', 'some_other_id', 'park_id'],
)
async def test_marketplace_is_disabled_for_park(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert response.status == 200
    assert response.json() == {
        **util.get_expected_offer_response(load_json),
        'is_available': False,
        'is_avaliable': False,
        'problem_description': {
            'code': 'marketplace_is_disabled_for_park',
            'localized_message': 'marketplace_is_disabled_for_park-tr',
        },
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_expired_offer(
        taxi_contractor_merch,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        status = 404 if offer_id_type == MUTABLE else 400
        return aiohttp.web.json_response(
            status=status, data={'code': '', 'message': ''},
        )

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert mock_driver_profiles.driver_profiles.times_called == 0

    assert response.status == 404
    assert response.json() == {
        'problem_description': {
            'code': 'offer_changed_or_expired',
            'localized_message': 'offer_changed_or_expired-tr',
        },
        'code': 'not_found',
        'message': 'Offer not found',
    }


RETRIEVE_BY_PROFILES_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'park_id_one_offer_total_limit_excceded',
            'data': {'unique_driver_id': 'some_uniq_id'},
        },
    ],
}

RETRIEVE_BY_PROFILES_RESPONSE_NO_UNIQ = {
    'uniques': [
        {'park_driver_profile_id': 'park_id_one_offer_total_limit_excceded'},
    ],
}

RETRIEVE_BY_UNIQUES_RESPONSE = {
    'profiles': [
        {
            'unique_driver_id': 'some_uniq_id',
            'data': [
                {
                    'park_id': 'park_id',
                    'driver_profile_id': 'one_offer_total_limit_excceded',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
                {
                    'park_id': 'park_id2',
                    'driver_profile_id': 'some_driver',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
            ],
        },
    ],
}

RETRIEVE_BY_UNIQUES_RESPONSE_1_DRIVER = {
    'profiles': [
        {
            'unique_driver_id': 'some_uniq_id',
            'data': [
                {
                    'park_id': 'park_id',
                    'driver_profile_id': 'one_offer_total_limit_excceded',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
            ],
        },
    ],
}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    'meta_info, retrieve_by_profiles_response, '
    'retrieve_by_uniques_response, expected_problem_description',
    [
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            {
                'code': 'one_offer_per_unique_driver_total_limit_excceded',
                'localized_message': (
                    'one_offer_per_unique_driver_total_limit_excceded-tr'
                ),
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_excceded',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE_NO_UNIQ,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            {
                'code': 'some_error_occured',
                'localized_message': 'some_error_occured-tr',
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='no_unique_driver',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE_1_DRIVER,
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_unreached_1',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 3},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_unreached_2',
        ),
    ],
)
async def test_unique_driver_limits(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        mock_taximeter_xservice,
        mock_unique_drivers,
        offer_id_type,
        meta_info,
        retrieve_by_profiles_response,
        retrieve_by_uniques_response,
        expected_problem_description,
):
    mock_unique_drivers.retrieve_by_profiles_response = (
        retrieve_by_profiles_response
    )
    mock_unique_drivers.retrieve_by_uniques_response = (
        retrieve_by_uniques_response
    )
    mock_taximeter_xservice.driver_exams_retrieve_response = {
        'dkvu_exam': {'summary': {'is_blocked': False}},
    }

    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        response = load_json(FEEDS_RESPONSE_JSON)
        response['feed'][0]['payload']['meta_info'].update(meta_info)
        return response

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={
            **HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'one_offer_total_limit_excceded',
        },
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1

    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)
    if expected_problem_description:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': False,
            'is_avaliable': False,
            'problem_description': expected_problem_description,
        }

    assert response.json() == expected_offer_response


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    'exams_response, is_blocked_by_dkvu',
    [
        ({'dkvu_exam': {'summary': {'is_blocked': True}}}, True),
        ({'dkvu_exam': {'summary': {'is_blocked': False}}}, False),
        ({'dkvu_exam': {'summary': {}}}, False),
        ({'dkvu_exam': {}}, False),
        ({}, False),
    ],
)
async def test_dkvu(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        mock_taximeter_xservice,
        mock_unique_drivers,
        offer_id_type,
        exams_response,
        is_blocked_by_dkvu,
):
    mock_taximeter_xservice.driver_exams_retrieve_response = exams_response
    if not is_blocked_by_dkvu:
        mock_unique_drivers.retrieve_by_profiles_response = (
            RETRIEVE_BY_PROFILES_RESPONSE
        )
        mock_unique_drivers.retrieve_by_uniques_response = (
            RETRIEVE_BY_UNIQUES_RESPONSE
        )

    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        response = load_json(FEEDS_RESPONSE_JSON)
        response['feed'][0]['payload']['meta_info'].update(
            {'total_per_unique_driver_limit': 3},
        )
        return response

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={
            **HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'one_offer_total_limit_excceded',
        },
    )

    expected_offer_response = util.get_expected_offer_response(load_json)
    if is_blocked_by_dkvu:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': False,
            'is_avaliable': False,
            'problem_description': {
                'code': 'drivers_license_is_not_verified',
                'localized_message': 'drivers_license_is_not_verified-tr',
            },
        }

    assert response.json() == expected_offer_response
    assert mock_driver_profiles.driver_profiles.times_called == 1


METRICS_BY_IDS = {
    MUTABLE: 'cannot-buy-reason',
    IMMUTABLE: 'cannot-buy-reason-by-immutable-offer-id',
}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.experiments3()
async def test_cannot_buy_metrics(
        taxi_contractor_merch,
        taxi_contractor_merch_monitor,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    mock_fleet_transactions_api.balance = '200'
    sensor = METRICS_BY_IDS[offer_id_type]

    metrics_before = await taxi_contractor_merch_monitor.get_metrics(sensor)

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert response.status == 200
    assert response.json() == {
        **util.get_expected_offer_response(load_json),
        'is_available': False,
        'is_avaliable': False,
        'problem_description': {
            'code': 'no_promocodes_left',
            'localized_message': 'no_promocodes_left-tr',
        },
    }

    metrics_after = await taxi_contractor_merch_monitor.get_metrics(sensor)

    if metrics_before[sensor] is None:
        metrics_before[sensor] = {'no_promocodes_left': 1}
    elif 'no_promocodes_left' not in metrics_before[sensor]:
        metrics_before[sensor]['no_promocodes_left'] = 1
    else:
        metrics_before[sensor]['no_promocodes_left'] += 1

    assert metrics_before == metrics_after
    assert mock_driver_profiles.driver_profiles.times_called == 1


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
async def test_expiration_params_passthrough(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    feeds_response = load_json('responses/feeds_response_with_meta.json')

    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        assert request.json['channels'] == [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'experiment:contractor_merch_offer_matched',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ]
        if offer_id_type == MUTABLE:
            assert request.json['feed_id'] == 'feed-id-1'
        else:
            assert request.json['package_ids'] == ['feeds-admin-id-1']

        return feeds_response

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    assert content == util.get_expected_offer_response(load_json, True)

    assert mock_driver_profiles.driver_profiles.times_called == 1


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_ok_without_place_id(
        taxi_contractor_merch,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_driver_tags,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        load_json,
        offer_id_type,
):
    feeds_response = load_json('responses/feeds_response.json')
    feeds_response['feed'][0]['payload'].pop('place_id')

    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        assert request.json['channels'] == [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'experiment:contractor_merch_offer_matched',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ]

        if offer_id_type == MUTABLE:
            assert request.json['feed_id'] == 'feed-id-1'
        else:
            assert request.json['package_ids'] == ['feeds-admin-id-1']

        return feeds_response

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert response.status == 200
    content = response.json()
    expected_offer = util.get_expected_offer_response(load_json)
    expected_offer['offer']['offer_data'].pop('place_id')
    assert content == expected_offer
