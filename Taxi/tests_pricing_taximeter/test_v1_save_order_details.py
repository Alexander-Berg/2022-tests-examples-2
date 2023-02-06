# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines
# flake8: noqa F401
import pytest
import copy

from tests_pricing_taximeter.plugins.mock_order_core import mock_order_core
from tests_pricing_taximeter.plugins.mock_order_core import order_core
from tests_pricing_taximeter.plugins.mock_order_core import OrderIdRequestType

TAXIMETER_APP = 'Taximeter 9.99 (4321)'


@pytest.mark.parametrize(
    'order_id, code, valid, case, driver_subvention, quasifixed',
    [
        ('alias_id_testcase_not_found_order', 404, None, [], 0, {}),
        ('alias_id_testcase_no_pricing_data', 404, None, [], 0, {}),
        ('alias_id_testcase_normal_order_invalid', 200, False, [], 0, {}),
        ('alias_id_testcase_normal_order_valid', 200, True, [], 0, {}),
        ('alias_id_testcase_normal_order_valid', 200, True, [], 20, {}),
        (
            'alias_id_testcase_normal_order_valid',
            200,
            True,
            ['fail_dp'],
            0,
            {},
        ),
        (
            'alias_id_testcase_normal_order_valid',
            200,
            True,
            ['quasifixed_exp'],
            0,
            {},
        ),
        (
            'alias_id_testcase_normal_order_valid',
            200,
            True,
            ['quasifixed_exp', 'fixed_offer'],
            0,
            {
                'log': 'Quasifixed result: user=2273239.5, driver=133.5',
                'bb`': 'Quasifixed price: order_id=normal_order route B-B\' - dist = 2046m  time = 307s',
                'ab': 'Quasifixed price: order_id=normal_order route A-B - dist = 2046m  time = 307s',
                'b`b': 'Quasifixed price: order_id=normal_order route B\'-B - dist = 2046m  time = 307s',
                'ab`': 'Quasifixed price: order_id=normal_order route A-B\' - dist = 2046m  time = 307s',
                'meta': '"Quasifixed_metadata": { {"user":{"answer":42.0},"driver":{}}}',
            },
        ),
        (
            'alias_id_testcase_normal_order_valid',
            200,
            True,
            ['quasifixed_exp', 'fixed_offer', 'use_quasifix'],
            0,
            {
                'log': 'Quasifixed result: user=2273239.5, driver=133.5',
                'bb`': 'Quasifixed price: order_id=normal_order route B-B\' - dist = 2046m  time = 307s',
                'ab': 'Quasifixed price: order_id=normal_order route A-B - dist = 2046m  time = 307s',
                'b`b': 'Quasifixed price: order_id=normal_order route B\'-B - dist = 2046m  time = 307s',
                'ab`': 'Quasifixed price: order_id=normal_order route A-B\' - dist = 2046m  time = 307s',
                'meta': '"Quasifixed_metadata": { {"user":{"answer":42.0},"driver":{}}}',
            },
        ),
        (
            'alias_id_testcase_normal_order_valid',
            200,
            True,
            ['fixed_offer'],
            0,
            {},
        ),
        ('alias_id_testcase_paid_supply_valid', 200, True, [], 0, {}),
        ('alias_id_testcase_fixprice_transfer_valid', 200, True, [], 0, {}),
        (
            'alias_id_testcase_taximeter_reset_transfer_valid',
            200,
            True,
            [],
            0,
            {},
        ),
        (
            'alias_id_testcase_using_trip_distance_time_on_fixprice',
            200,
            True,
            [],
            0,
            {},
        ),
        (
            'alias_id_testcase_using_trip_distance_time_on_taximeter',
            200,
            True,
            [],
            0,
            {},
        ),
    ],
    ids=[
        'not_found_order',
        'no_pricing_data',
        'normal_order_invalid',
        'normal_order_valid',
        'normal_order_valid_with_subvention',
        'normal_order_valid_with_subvention_fail',
        'normal_order_valid_with_quasifixed_exp',
        'normal_order_valid_quasifixed_works',
        'normal_order_valid_quasifixed_use',
        'normal_order_valid_fixed_offer',
        'paid_supply_valid',
        'fixed_price_transfer_valid',
        'taximeter_reset_transfer_valid',
        'using_trip_distance_time_on_fixprice',
        'using_trip_distance_time_on_taximeter',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize('cost_type', ['taximeter', 'recalculated'])
@pytest.mark.now('2020-10-27T18:30:00Z')
async def test_v1_save_order_details(
        taxi_pricing_taximeter,
        taxi_pricing_taximeter_monitor,
        order_id,
        code,
        testpoint,
        load_json,
        valid,
        cost_type,
        mockserver,
        experiments3,
        case,
        mock_yamaps_router,
        mongodb,
        driver_subvention,
        quasifixed,
        order_core,
        mock_order_core,
):
    taximeter_data = load_json('taximeter_data.json')
    order_data = taximeter_data[order_id]

    taximeter_message = load_json('taximeter_messages.json').get(order_id, {})
    validation_message = load_json('validation_messages.json').get(
        order_id, {},
    )
    if 'use_quasifix' in case:
        validation_message['extra'] = {
            'quasifixed_params': {
                'driver': {
                    'distance_a_b': 2046.0,
                    'distance_a_bf': 2046.0,
                    'distance_b_bf': 2046.0,
                    'distance_bf_b': 2046.0,
                    'fixed_price_boarding': 100.0,
                    'fixed_price_distance': 100.0,
                    'fixed_price_time': 100.0,
                },
                'user': {
                    'distance_a_b': 2046.0,
                    'distance_a_bf': 2046.0,
                    'distance_b_bf': 2046.0,
                    'distance_bf_b': 2046.0,
                    'fixed_price_boarding': 150.0,
                    'fixed_price_distance': 150.0,
                    'fixed_price_time': 150.0,
                },
            },
            'replaced_driver_price': 133.5,
            'replaced_user_price': 133.5,
        }
        validation_message['user_final_price'] = 2273239.5
        validation_message['user_price_delta_list'][3]['components'][
            1
        ] = 2273106.0
        validation_message['user_price_meta'] = {'answer': 42}

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='final_cost_pricing_settings',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={'use_antifraud': False, 'cost_type': cost_type},
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='pa_reset_fixed_price_by_time',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={
            'enabled': True,
            'replace_prices': False,
            'min_fixed_duration': 600.0,
            'time_coeff_on_transporting': 0.2,
            'time_coeff_on_order': 0.3,
            'max_speed_kph': 150.0,
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='pa_restore_fixed_price_by_time',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={
            'enabled': True,
            'replace_prices': False,
            'min_fixed_duration': 600.0,
            'time_coeff_on_transporting': 0.7,
            'distance_ratio_for_broken_track': 0.2,
            'time_ratio_for_broken_track': 0.2,
        },
    )
    if 'use_quasifix' in case:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='quasifixed_price_enabled',
            consumers=['pricing-data-preparer/save_order_details'],
            clauses=[],
            default_value={'enabled': True, 'use': True},
        )
    elif 'quasifixed_exp' in case:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='quasifixed_price_enabled',
            consumers=['pricing-data-preparer/save_order_details'],
            clauses=[],
            default_value={'enabled': True},
        )

    if 'fixed_offer' in case:
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {'$set': {'order.pricing_data.fixed_price': True}},
        )
    if order_id == 'alias_id_testcase_normal_order_invalid':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order_invalid'},
            {'$set': {'auction.iteration': 1}},
        )

    @testpoint('taximeter_message')
    def tp_taximeter_message(data):
        assert data == taximeter_message

    @testpoint('validation_message')
    def tp_validation_message(data):
        assert data == validation_message

    @testpoint('recalc_prices_mismatch')
    def tp_recalc_prices_mismatch(data):
        assert data == valid

    @testpoint('auction_check')
    def tp_auction_check(data):
        pass

    @testpoint('A-B')
    def route_ab_test(data):
        assert data['dist'] == 2046
        assert data['time'] == 307
        assert data['point_from'] == {'lat': 60.0, 'lon': 40.0}
        assert data['point_to'] == {'lat': 61.0, 'lon': 41.0}

    @testpoint('A-B\'')
    def route_abf_test(data):
        assert data['dist'] == 2046
        assert data['time'] == 307
        assert data['point_from'] == {'lat': 60.0, 'lon': 40.0}
        assert data['point_to'] == {'lat': 48.070869, 'lon': 46.339191}

    @testpoint('B-B\'')
    def route_bbf_test(data):
        assert data['dist'] == 2046
        assert data['time'] == 307
        assert data['point_from'] == {'lat': 61.0, 'lon': 41.0}
        assert data['point_to'] == {'lat': 48.070869, 'lon': 46.339191}

    @testpoint('B\'-B')
    def route_bfb_test(data):
        assert data['dist'] == 2046
        assert data['time'] == 307
        assert data['point_from'] == {'lat': 48.070869, 'lon': 46.339191}
        assert data['point_to'] == {'lat': 61.0, 'lon': 41.0}

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={'order_id': order_id, 'taximeter_app': TAXIMETER_APP},
        json=order_data,
    )

    assert response.status_code == code

    assert tp_recalc_prices_mismatch.has_calls == (valid is not None)

    if code != 200 and order_id != 'alias_id_testcase_no_pricing_data':
        assert not tp_taximeter_message.times_called
        assert not tp_validation_message.times_called
    elif order_id == 'alias_id_testcase_no_pricing_data':
        assert tp_taximeter_message.times_called == 1
        assert not tp_validation_message.times_called
    else:
        assert tp_taximeter_message.times_called == 1
        assert tp_validation_message.times_called == 1
    assert not tp_auction_check.times_called

    if code == 200:
        original_price = {
            'driver': {
                'total': validation_message['driver_final_price'],
                'meta': validation_message['driver_price_meta'],
                'extra': {},
            },
            'user': {
                'total': validation_message['user_final_price'],
                'meta': validation_message['user_price_meta'],
                'extra': {
                    'without_surge': validation_message['user_final_price'],
                },
            },
        }

        resp = response.json()

        if cost_type == 'taximeter':
            taximeter_user_cost = order_data['ride']['user']['rounded_price']
            taximeter_driver_cost = order_data['ride']['driver'][
                'rounded_price'
            ]
            expected_final_price = {
                'driver': {
                    'meta': {},
                    'total': taximeter_driver_cost,
                    'extra': {},
                },
                'user': {
                    'meta': {},
                    'total': taximeter_user_cost,
                    'extra': {'without_surge': taximeter_user_cost},
                },
            }
            # crutch for different rounding_factor
            if order_id == 'alias_id_testcase_normal_order_invalid':
                resp['price']['user']['extra']['without_surge'] = round(
                    resp['price']['user']['extra']['without_surge'] + 0.5, 0,
                )
        else:
            expected_final_price = original_price

        assert 'recalculated' in resp['price_verifications']['uuids']
        resp.pop('price_verifications')  # because uuid

        if 'use_quasifix' in case:
            expected_final_price['user']['meta'] = {'answer': 42}
            expected_final_price['user']['total'] = 2273239.5
            expected_final_price['user']['extra']['without_surge'] = 2273239.5

        assert resp == {
            'price': expected_final_price,
            'payment_type': 'payment_type',
        }

    if 'quasifixed_exp' in case and 'fixed_offer' in case:
        await route_ab_test.wait_call()
        await route_abf_test.wait_call()
        await route_bbf_test.wait_call()
        await route_bfb_test.wait_call()
    else:
        assert not route_ab_test.has_calls
        assert not route_abf_test.has_calls
        assert not route_bbf_test.has_calls
        assert not route_bfb_test.has_calls

    if code == 200:
        async with taxi_pricing_taximeter.capture_logs() as capture:
            response = await taxi_pricing_taximeter.post(
                'v1/save_order_details',
                params={'order_id': order_id, 'taximeter_app': TAXIMETER_APP},
                json=order_data,
            )
            assert response.status_code == 200

        logs = capture.select(link=response.headers['x-yarequestid'])
        for log in logs:
            txt = log['text']
            if 'Quasifixed result' in txt:
                assert txt == quasifixed['log']
            elif 'Quasifixed price experiment is working now' in txt:
                assert 'quasifixed_exp' in case and 'fixed_offer' in case
            elif 'Quasifixed price experiment is switched off' in txt:
                assert (
                    'quasifixed_exp' not in case or 'fixed_offer' not in case
                )
            elif 'Quasifixed price: order_id' in txt:
                assert 'quasifixed_exp' in case and 'fixed_offer' in case
                if 'B-B\'' in txt:
                    assert txt == quasifixed['bb`']
                elif 'A-B\'' in txt:
                    assert txt == quasifixed['ab`']
                elif 'B\'-B' in txt:
                    assert txt == quasifixed['b`b']
                elif 'A-B' in txt:
                    assert txt == quasifixed['ab']
                else:
                    print('Unexpected log: ', txt)
                    assert False
            elif 'Quasifixed_metadata' in txt:
                assert 'quasifixed_exp' in case and 'fixed_offer' in case
                assert txt == quasifixed['meta']
            elif 'Running testpoint validation_message' in txt:
                pass
            elif 'Forced set FinalCostPricingSettings' in txt:
                pass
            elif (
                'uasifix' in txt
                and 'Exception' not in txt
                and 'quasifixed_price_enabled' not in txt
            ):
                print('Unexpected log: ', txt)
                assert False


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2020-10-27T18:30:00Z')
async def test_read_from_order_core(
        taxi_pricing_taximeter,
        load_json,
        experiments3,
        mock_order_core,
        order_core,
        mock_yamaps_router,
):
    taximeter_data = load_json('taximeter_data.json')
    order_data = taximeter_data['alias_id_testcase_normal_order_valid']

    experiments3.add_config(
        consumers=['pricing-data-preparer/pricing_components'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='read_order_proc_from_order_core',
        default_value={
            '__default__': 'mongo',
            'save_order_details': 'order_core',
        },
    )

    order_core.set_expected_key(
        'alias_id_testcase_normal_order_valid',
        OrderIdRequestType.alias_id,
        require_latest=True,
    )

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={
            'order_id': 'alias_id_testcase_normal_order_valid',
            'taximeter_app': TAXIMETER_APP,
        },
        json=order_data,
    )

    assert response.status_code == 200

    assert mock_order_core.times_called == 1


DEFAULT_ALIAS_WITH_FRAUD = 'default_alias_with_fraud'
DEFAULT_ORDER_ID = 'order_with_fraud'

PRICE_CHANGED_COMMUNICATION = {
    'message': {
        'message': {
            'keyset': 'taximeter_backend_driver_messages',
            'key': 'pricing_antifraud_price_changed',
            'params': {'price': '100.00 ₽'},
        },
        'flags': ['high_priority'],
    },
}


@pytest.mark.parametrize(
    'alias_id, checking_failed, fill_recalculated_section, modifications',
    [
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_config']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['disable_config']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['disable_antifraud']),
        ('mixed_calc_type', False, False, []),
        ('calc_type_is_taximeter', False, False, []),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_payment_tech']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['set_payment_type_to_cash']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_status_updates']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_status_driving']),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            False,
            False,
            ['increase_min_fixed_duration'],
        ),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            False,
            False,
            ['decrease_coeff_on_transporting'],
        ),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['decrease_coeff_on_order']),
        ('big_taximeter_price', False, False, []),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            True,
            True,
            ['disable_final_cost_settings'],
        ),
        (DEFAULT_ALIAS_WITH_FRAUD, True, True, []),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['add_cargo']),
        ('fraud_with_paid_supply', True, True, ['set_paid_supply']),
        (DEFAULT_ALIAS_WITH_FRAUD, True, True, ['remove_status_transporting']),
        (DEFAULT_ALIAS_WITH_FRAUD, True, False, ['only_logging']),
        ('fraud_with_high_speed', True, True, []),
    ],
    ids=[
        'without_antifraud_settings',
        'config_disabled',
        'antifraud_disabled',
        'mixed_calc_type',
        'taximeter_ride',
        'missed_payment_tech',
        'payment_type_is_cash',
        'missed_status_updates',
        'missed_status_driving',
        'small_fixed_duration',
        'big_time_on_transporting',
        'big_time_on_order',
        'taximeter_price_too_big',
        'success_and_log',
        'skipped_for_cargo',
        'success_and_replace',
        'success_and_replace_with_paid_supply',
        'missed_status_transporting',
        'only_logging',
        'with_high_speed',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2021-04-17T17:07:00Z')
async def test_antifraud_reset_fixed_price_by_time(
        taxi_pricing_taximeter,
        alias_id,
        checking_failed,
        fill_recalculated_section,
        modifications,
        testpoint,
        load_json,
        mockserver,
        experiments3,
        mongodb,
        order_core,
        mock_order_core,
):
    if 'set_payment_type_to_cash' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$set': {'payment_tech': {'type': 'cash'}}},
        )
    if 'remove_payment_tech' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID}, {'$unset': {'payment_tech': ''}},
        )
    if 'remove_status_updates' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$unset': {'order_info.statistics.status_updates': ''}},
        )
    if 'remove_status_driving' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$unset': {'order_info.statistics.status_updates.$[cat]': ''}},
            array_filters=[{'cat.t': 'driving'}],
        )
    if 'remove_status_transporting' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$unset': {'order_info.statistics.status_updates.$[cat]': ''}},
            array_filters=[{'cat.t': 'transporting'}],
        )
    with_paid_supply = 'set_paid_supply' in modifications
    if with_paid_supply:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$set': {'order.performer.paid_supply': True}},
        )

    if 'remove_config' not in modifications:
        experiments3.add_config(
            match={
                'predicate': {'type': 'true'},
                'enabled': ('disable_config' not in modifications),
            },
            name='pa_reset_fixed_price_by_time',
            consumers=['pricing-data-preparer/save_order_details'],
            clauses=[],
            default_value={
                'enabled': ('disable_antifraud' not in modifications),
                'replace_prices': ('only_logging' not in modifications),
                'min_fixed_duration': 600.0 + (
                    3600.0
                    if ('increase_min_fixed_duration' in modifications)
                    else 0.0
                ),
                'time_coeff_on_transporting': 0.2 - (
                    0.19
                    if ('decrease_coeff_on_transporting' in modifications)
                    else 0.0
                ),
                'time_coeff_on_order': 0.3 - (
                    0.29
                    if ('decrease_coeff_on_order' in modifications)
                    else 0.0
                ),
                'max_speed_kph': 150.0,
            },
        )

    if 'add_cargo' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$set': {'order.request.cargo_ref_id': 'kakoytotrash'}},
        )

    disable_final_cost_settings = (
        'disable_final_cost_settings' in modifications
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='final_cost_pricing_settings',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={
            'use_antifraud': not disable_final_cost_settings,
            'cost_type': 'recalculated',
        },
    )

    replace_prices_in_response = (
        checking_failed
        and fill_recalculated_section
        and not disable_final_cost_settings
    )

    requests = load_json('taximeter_data.json')
    request = requests[alias_id]

    expected_taximeter_messages = []
    expected_taximeter_messages.append(
        load_json('taximeter_messages.json').get(alias_id, {}),
    )
    if checking_failed:
        expected_taximeter_messages.append(
            load_json('taximeter_messages_antifraud.json').get(alias_id, {}),
        )

    validation_message = load_json('validation_messages.json').get(
        alias_id, {},
    )
    if checking_failed:
        validation_message_antifraud = load_json(
            'validation_messages_antifraud.json',
        ).get(alias_id, {})

    if fill_recalculated_section:
        validation_message[
            'recalculated_distance'
        ] = validation_message_antifraud['recalculated_distance']
        validation_message['recalculated_time'] = validation_message_antifraud[
            'recalculated_time'
        ]
        validation_message[
            'recalculated_driver_price'
        ] = validation_message_antifraud['recalculated_driver_price']
        validation_message[
            'recalculated_user_price'
        ] = validation_message_antifraud['recalculated_user_price']
        validation_message[
            'recalculation_reason'
        ] = validation_message_antifraud['recalculation_reason']

    expected_validation_messages = []
    if checking_failed:
        expected_validation_messages.append(validation_message_antifraud)
    expected_validation_messages.append(validation_message)

    taximeter_messages = []
    validation_messages = []

    @testpoint('taximeter_message')
    def tp_taximeter_message(data):
        nonlocal taximeter_messages
        taximeter_messages.append(data)

    @testpoint('validation_message')
    def tp_validation_message(data):
        nonlocal validation_messages
        validation_messages.append(data)

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={'order_id': alias_id, 'taximeter_app': TAXIMETER_APP},
        json=request,
    )

    assert taximeter_messages == expected_taximeter_messages
    assert validation_messages == expected_validation_messages

    assert response.status_code == 200

    resp = response.json()

    if replace_prices_in_response:
        expected_price = 526.0 + (150.0 if with_paid_supply else 0)
        if alias_id == 'fraud_with_high_speed':
            expected_price = 310.0

        assert resp['price']['user']['total'] == expected_price
        assert resp['price']['driver']['total'] == expected_price

        assert resp['recalculated_reason'] == 'antifraud'

        expected_push = copy.deepcopy(PRICE_CHANGED_COMMUNICATION)
        expected_push['message']['message']['params']['price'] = (
            f'{expected_price:.2f}' + ' ₽'
        )
        expected_push['message']['id'] = (
            resp['price_changed_communication']['message']['id']
        )  # because uuid
        assert resp['price_changed_communication'] == expected_push
    else:
        assert (
            resp['price']['user']['total']
            == request['ride']['user']['rounded_price']
        )
        assert (
            resp['price']['driver']['total']
            == request['ride']['driver']['rounded_price']
        )
    assert 'recalculated' in resp['price_verifications']['uuids']
    assert ('antifraud' in resp['price_verifications']['uuids']) == (
        checking_failed and fill_recalculated_section
    )

    assert tp_taximeter_message.times_called == (2 if checking_failed else 1)
    assert tp_validation_message.times_called == (2 if checking_failed else 1)


@pytest.mark.parametrize(
    'alias_id, checking_failed, fill_recalculated_section, modifications',
    [
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_config']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['disable_config']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['disable_antifraud']),
        (DEFAULT_ALIAS_WITH_FRAUD, True, False, ['only_logging']),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            False,
            False,
            ['increase_min_fixed_duration'],
        ),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            False,
            False,
            ['increase_coeff_on_transporting'],
        ),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            True,
            True,
            ['disable_final_cost_settings'],
        ),
        (DEFAULT_ALIAS_WITH_FRAUD, True, True, []),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['decrease_distance_ratio']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['decrease_time_ratio']),
        ('mixed_calc_type', False, False, []),
        ('calc_type_is_fixed', False, False, []),
        (
            'big_taximeter_price',
            False,
            False,
            ['increase_distance_ratio', 'increase_time_ratio'],
        ),
        (DEFAULT_ALIAS_WITH_FRAUD, True, True, ['set_payment_type_to_cash']),
        (DEFAULT_ALIAS_WITH_FRAUD, False, False, ['remove_fixed_price']),
        (
            DEFAULT_ALIAS_WITH_FRAUD,
            False,
            False,
            ['remove_fixed_price_prices'],
        ),
        ('with_waiting_in_point_a', True, True, []),
        ('with_waiting_in_transit', False, False, []),
    ],
    ids=[
        'without_antifraud_settings',
        'config_disabled',
        'antifraud_disabled',
        'only_logging',
        'small_fixed_duration',
        'small_time_on_transporting',
        'success_and_log',
        'success_and_replace',
        'big_track_distance',
        'big_track_time',
        'mixed_calc_type',
        'fixed_ride',
        'fixed_price_too_small',
        'payment_type_is_cash',
        'without_offer',
        'change_destinations',
        'waiting_in_point_a',
        'waiting_in_transit',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2021-04-17T17:59:00Z')
async def test_antifraud_restore_fixed_price_by_time(
        taxi_pricing_taximeter,
        alias_id,
        checking_failed,
        fill_recalculated_section,
        modifications,
        testpoint,
        load_json,
        mockserver,
        experiments3,
        mongodb,
        order_core,
        mock_order_core,
):
    payment_type_is_cash = 'set_payment_type_to_cash' in modifications
    if payment_type_is_cash:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {'$set': {'payment_tech': {'type': 'cash'}}},
        )

    if 'remove_fixed_price' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID}, {'$unset': {'order.fixed_price': ''}},
        )

    if 'remove_fixed_price_prices' in modifications:
        mongodb.order_proc.update_one(
            {'_id': DEFAULT_ORDER_ID},
            {
                '$unset': {
                    'order.fixed_price.price': '',
                    'order.fixed_price.driver_price': '',
                },
            },
        )

    distance_ratio_for_broken_track = 0.2
    if 'decrease_distance_ratio' in modifications:
        distance_ratio_for_broken_track = 0.0
    elif 'increase_distance_ratio' in modifications:
        distance_ratio_for_broken_track = 1000.0

    time_ratio_for_broken_track = 0.2
    if 'decrease_time_ratio' in modifications:
        time_ratio_for_broken_track = 0.0
    elif 'increase_time_ratio' in modifications:
        time_ratio_for_broken_track = 1000.0

    if 'remove_config' not in modifications:
        experiments3.add_config(
            match={
                'predicate': {'type': 'true'},
                'enabled': ('disable_config' not in modifications),
            },
            name='pa_restore_fixed_price_by_time',
            consumers=['pricing-data-preparer/save_order_details'],
            clauses=[],
            default_value={
                'enabled': ('disable_antifraud' not in modifications),
                'replace_prices': ('only_logging' not in modifications),
                'min_fixed_duration': 600.0 + (
                    3600.0
                    if ('increase_min_fixed_duration' in modifications)
                    else 0.0
                ),
                'time_coeff_on_transporting': 0.7 + (
                    1.0
                    if ('increase_coeff_on_transporting' in modifications)
                    else 0.0
                ),
                'distance_ratio_for_broken_track': (
                    distance_ratio_for_broken_track
                ),
                'time_ratio_for_broken_track': time_ratio_for_broken_track,
            },
        )

    disable_final_cost_settings = (
        'disable_final_cost_settings' in modifications
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='final_cost_pricing_settings',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={
            'use_antifraud': not disable_final_cost_settings,
            'cost_type': 'recalculated',
        },
    )

    replace_prices_in_response = (
        checking_failed
        and fill_recalculated_section
        and not disable_final_cost_settings
    )

    requests = load_json('taximeter_data.json')
    request = requests[alias_id]

    expected_taximeter_messages = []
    expected_taximeter_messages.append(
        load_json('taximeter_messages.json').get(alias_id, {}),
    )
    if checking_failed:
        expected_taximeter_messages.append(
            load_json('taximeter_messages_antifraud.json').get(alias_id, {}),
        )

    validation_message = load_json('validation_messages.json').get(
        alias_id, {},
    )
    if checking_failed:
        validation_message_antifraud = load_json(
            'validation_messages_antifraud.json',
        ).get(alias_id, {})

    if fill_recalculated_section:
        validation_message[
            'recalculated_distance'
        ] = validation_message_antifraud['recalculated_distance']
        validation_message['recalculated_time'] = validation_message_antifraud[
            'recalculated_time'
        ]
        validation_message[
            'recalculated_driver_price'
        ] = validation_message_antifraud['recalculated_driver_price']
        validation_message[
            'recalculated_user_price'
        ] = validation_message_antifraud['recalculated_user_price']
        validation_message[
            'recalculation_reason'
        ] = validation_message_antifraud['recalculation_reason']

    expected_validation_messages = []
    if checking_failed:
        expected_validation_messages.append(validation_message_antifraud)
    expected_validation_messages.append(validation_message)

    taximeter_messages = []
    validation_messages = []

    @testpoint('taximeter_message')
    def tp_taximeter_message(data):
        nonlocal taximeter_messages
        taximeter_messages.append(data)

    @testpoint('validation_message')
    def tp_validation_message(data):
        nonlocal validation_messages
        validation_messages.append(data)

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={'order_id': alias_id, 'taximeter_app': TAXIMETER_APP},
        json=request,
    )

    assert taximeter_messages == expected_taximeter_messages
    assert validation_messages == expected_validation_messages

    waiting_in_a_delta = (
        113.0 if alias_id == 'with_waiting_in_point_a' else 0.0
    )
    waiting_in_transit_delta = (
        113.0 if alias_id == 'waiting_in_transit' else 0.0
    )
    waiting_deltas = waiting_in_a_delta + waiting_in_transit_delta

    assert response.status_code == 200

    resp = response.json()

    if replace_prices_in_response:
        assert resp['price']['user']['total'] == 750.0 + waiting_deltas
        assert resp['price']['driver']['total'] == 900.0 + waiting_deltas

        assert resp['recalculated_reason'] == 'antifraud'

        if waiting_deltas > 0:
            expected_price_str = (
                '863.00 ₽' if payment_type_is_cash else '1013.00 ₽'
            )
        else:
            expected_price_str = (
                '750.00 ₽' if payment_type_is_cash else '900.00 ₽'
            )

        expected_push = copy.deepcopy(PRICE_CHANGED_COMMUNICATION)
        expected_push['message']['message']['params'][
            'price'
        ] = expected_price_str
        expected_push['message']['id'] = (
            resp['price_changed_communication']['message']['id']
        )  # because uuid
        assert resp['price_changed_communication'] == expected_push
    else:
        assert (
            resp['price']['user']['total']
            == request['ride']['user']['rounded_price']
        )
        assert (
            resp['price']['driver']['total']
            == request['ride']['driver']['rounded_price']
        )
    assert 'recalculated' in resp['price_verifications']['uuids']
    assert ('antifraud' in resp['price_verifications']['uuids']) == (
        checking_failed and fill_recalculated_section
    )

    assert tp_taximeter_message.times_called == (2 if checking_failed else 1)
    assert tp_validation_message.times_called == (2 if checking_failed else 1)


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2020-10-27T18:30:00Z')
@pytest.mark.config(
    PRICING_SAVE_AGENT_ORDERS_DETAILS=True,
    PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS={
        'agent/v1/save_order_details': {
            'services': {
                'patterns': ['additional_foo', 'only_for_agent_foo'],
                'tanker': {'keyset': 'tariff'},
            },
        },
        'v1/save_order_details': {
            'services': {
                'patterns': ['additional_foo', 'only_for_response_foo'],
                'tanker': {'keyset': 'tariff'},
            },
        },
    },
)
async def test_split_price_details(
        taxi_pricing_taximeter, stq, load_json, order_core, mock_order_core,
):
    def _make_details_item(name, price):
        return {
            'name': name,
            'price': price,
            'text': {'keyset': 'tariff', 'tanker_key': name},
        }

    def _make_details(metadata, keys):
        items = []
        for key in keys:
            value = metadata.get(key, None)
            if value:
                items.append(_make_details_item(key, value))
        return {'services': items}

    expected_metadata = {
        'additional_foo': 1.0,
        'only_for_agent_foo': 2.0,
        'only_for_response_foo': 3.0,
    }

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={
            'order_id': 'alias_id_testcase_normal_order_valid',
            'taximeter_app': TAXIMETER_APP,
        },
        json=load_json('taximeter_data.json'),
    )
    assert response.status_code == 200

    expected_details = _make_details(
        expected_metadata, ('additional_foo', 'only_for_response_foo'),
    )

    data = response.json()
    driver = data['price']['driver']
    user = data['price']['user']
    for each in (driver, user):
        assert each['meta'] == expected_metadata
        assert each['additional_payloads']['details'] == expected_details

    expected_agent_details = _make_details(
        expected_metadata, ('additional_foo', 'only_for_agent_foo'),
    )
    expected_agent_details.update({'requirements': []})

    assert stq.agent_orders_save_price_details.times_called == 1
    next_task = stq.agent_orders_save_price_details.next_call()
    assert next_task['queue'] == 'agent_orders_save_price_details'
    kwargs = next_task['kwargs']
    assert kwargs['order_id'] == 'normal_order'
    assert kwargs['calculated_at'] == '2020-10-27T18:30:00+00:00'
    assert kwargs['details'] == expected_agent_details


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_price_without_surge(
        taxi_pricing_taximeter, load_json, order_core, mock_order_core,
):
    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={
            'order_id': 'alias_id_testcase_normal_order_valid',
            'taximeter_app': TAXIMETER_APP,
        },
        json=load_json('taximeter_data.json'),
    )
    assert response.status_code == 200

    resp = response.json()
    driver = resp['price']['driver']
    assert driver['total'] == 133.5
    assert 'extra' in driver
    assert 'without_surge' not in driver['extra']

    user = resp['price']['user']
    assert user['total'] == 133.5
    assert 'extra' in user
    assert 'without_surge' in user['extra']
    assert user['extra']['without_surge'] == 153.5


@pytest.mark.parametrize(
    'alias_id, order_proc_alternative_type, '
    'combo_order_was_matched, driver_discount_disabled',
    [
        (
            'combo_order_alias',
            None,
            None,
            False,
        ),  # without changes (keep discount)
        (
            'combo_order_alias',
            'some_alternative_type',
            False,
            False,
        ),  # without changes (keep discount)
        (
            'combo_order_alias',
            'combo',
            False,
            True,
        ),  # increase price (disable discount)
        (
            'combo_order_alias',
            'some_alternative_type',
            False,
            False,
        ),  # without changes (keep discount)
        (
            'combo_order_disabled_discount',
            'combo',
            False,
            True,
        ),  # without changes (discount_was_disabled)
    ],
    ids=[
        'without_combo_flags',
        'not_combo',
        'compensate_combo_discount',
        'keep_combo_discount',
        'discount_was_not_enabled',
    ],
)
@pytest.mark.config(COMBO_ALTERNATIVE_TYPES=['combo', 'smaller_combo'])
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
async def test_recalculate_combo_order(
        taxi_pricing_taximeter,
        load_json,
        experiments3,
        mongodb,
        alias_id,
        order_proc_alternative_type,
        combo_order_was_matched,
        driver_discount_disabled,
        order_core,
        mock_order_core,
):
    if alias_id == 'combo_order_disabled_discount':
        path = 'order.pricing_data.user.data.combo_offers_data.apply_combo_discount_for_driver'
        mongodb.order_proc.update_one(
            {'_id': 'combo_order'}, {'$set': {path: False}},
        )

    alternative_type_path = 'order.calc.alternative_type'
    if order_proc_alternative_type is None:
        mongodb.order_proc.update_one(
            {'_id': 'combo_order'}, {'$unset': {alternative_type_path: True}},
        )
    else:
        mongodb.order_proc.update_one(
            {'_id': 'combo_order'},
            {'$set': {alternative_type_path: order_proc_alternative_type}},
        )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='final_cost_pricing_settings',
        consumers=['pricing-data-preparer/save_order_details'],
        clauses=[],
        default_value={'use_antifraud': False, 'cost_type': 'recalculated'},
    )

    request_json = load_json('taximeter_data.json')
    if combo_order_was_matched is not None:
        request_json['combo_order_was_matched'] = combo_order_was_matched

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        params={'order_id': alias_id, 'taximeter_app': TAXIMETER_APP},
        json=request_json,
    )
    assert response.status_code == 200

    expected_user_price = 675.0
    expected_driver_price = 900.0 if driver_discount_disabled else 825.0

    resp = response.json()
    assert resp['price']['user']['total'] == expected_user_price
    assert resp['price']['driver']['total'] == expected_driver_price

    if (
            driver_discount_disabled
            and alias_id != 'combo_order_disabled_discount'
    ):
        assert 'recalculated_reason' in resp
        assert resp['recalculated_reason'] == 'refund_combo_discount'
    else:
        assert 'recalculated_reason' not in resp
