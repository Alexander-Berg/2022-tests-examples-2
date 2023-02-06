from copy import deepcopy
import datetime
import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_MATCH_SWITCH
from protocol.ordercommit import order_commit_common


PERSONAL_WALLET_BALANCES_URL = '/personal_wallet/v1/balances'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.fixture
def ordercommit_services(mockserver, load_binary, load_json):
    class context:
        experiments = ['forced_surge']
        client = {
            'name': 'iphone',
            'version': [3, 61, 4830],
            'platform_version': [10, 1, 1],
        }
        payment_type = 'cash'
        surge_tariff_classes = ['econom']
        multiclass_pricing_storage_expected_request = None
        multiclass_pricing_storage_response = {}
        multiclass_pricing_storage_request_got = False
        multiclass_pricing_storage_emulate_failure = False

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route.protobuf'),
            content_type='application/x-protobuf',
        )

    return context


@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_order_no_user_uid(
        taxi_protocol, mockserver, load, db, now,
):
    request = {'id': USER_ID, 'orderid': '8c83b49edb274ce0992f337061047400'}

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'order_id,surge_value,expected_code',
    [
        ('surge_12', 1.2, 200),
        ('surge_12', 1.1, 200),
        ('surge_12', 1.3, 200),
        ('surge_12_future', 1.3, 406),
    ],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_forced_surge(
        taxi_protocol,
        ordercommit_services,
        order_id,
        surge_value,
        expected_code,
        mockserver,
        load_json,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    ordercommit_services.client = {
        'name': 'iphone',
        'version': [3, 61, 4830],
        'platform_version': [10, 1, 1],
    }

    pricing_data_preparer.set_fixed_price(enable=False, category='econom')
    pricing_data_preparer.set_user_surge(surge_value)

    ordercommit_services.surge_value = surge_value
    ordercommit_services.experiments = ['forced_surge']
    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_id, offer_deleted, expected_code, none_or_expected_response',
    [
        ('fixed_price_0', False, 200, None),
        ('fixed_price_1_offer_deleted', True, 406, None),
        ('fixed_price_2_same_payment_type_in_offer', False, 200, None),
        (
            'fixed_price_3_different_payment_type_in_offer',
            False,
            # https://st.yandex-team.ru/EFFICIENCYDEV-2549#5cd9aa30c33cd5001ebc17dc
            200,
            None,
        ),
        (
            'fixed_price_4_different_payment_type_in_offer_and_paid_supply',
            False,
            # https://st.yandex-team.ru/EFFICIENCYDEV-2867
            406,
            {
                'error': {
                    'code': 'PAYMENT_TYPE_MISMATCHES_OFFER',
                    'text': 'Please retry order in a few seconds',
                },
            },
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'common_errors.PAYMENT_TYPE_MISMATCHES_OFFER': {
            'ru': 'Please retry order in a few seconds',
        },
    },
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('fixed_price')
@ORDER_OFFERS_MATCH_SWITCH
@pytest.mark.now('2022-06-06T16:00:00+0300')
def test_ordercommit_fixed_price(
        taxi_protocol,
        ordercommit_services,
        order_id,
        offer_deleted,
        expected_code,
        none_or_expected_response,
        mockserver,
        load_json,
        mock_order_offers,
        order_offers_match_enabled,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        request_json = json.loads(request.get_data())
        assert 'zone' in request_json and request_json['zone']
        pdp_response = load_json('pdp_v2_prepare_response.json')
        return pdp_response

    if not offer_deleted:
        mock_order_offers.set_offer_to_match(f'offer-{order_id}')

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )
    assert response.status_code == expected_code
    if none_or_expected_response is not None:
        assert response.json() == none_or_expected_response

    mock_order_offers.mock_match_offer.times_called == (
        1 if order_offers_match_enabled else 0
    )
    if order_offers_match_enabled:
        match_request = mock_order_offers.last_match_request
        assert match_request == {
            'filters': {
                'order': {
                    'classes': ['econom'],
                    # +100 seconds from mocked now moment
                    'due': datetime.datetime(2022, 6, 6, 13, 1, 40),
                    'requirements': {},
                    'route': [[37.58, 55.73], [37.5, 55.7]],
                },
                'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
                'offer_id': f'offer-{order_id}',
            },
        }


@pytest.mark.order_experiments('fixed_price')
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_ordercommit_fixed_price_for_corpweb(
        taxi_protocol,
        db,
        mockserver,
        ordercommit_services,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    ordercommit_services.experiments = ['fixed_price']
    ordercommit_services.client = {
        'name': 'corpweb',
        'platform_version': [0, 0, 0],
        'version': [2, 0, 0],
    }
    ordercommit_services.payment_type = 'corp'
    request = {'id': USER_ID, 'orderid': '82862422308caaaaaaaaaaaab248ea6a'}

    @mockserver.json_handler('/corp_integration_api/corp_paymentmethods')
    def mock_corp_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-12345',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'user_id',
                    'client_comment': 'comment',
                    'currency': 'RUB',
                },
            ],
        }

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    proc = db.order_proc.find_one({'_id': '82862422308caaaaaaaaaaaab248ea6a'})
    assert proc['commit_state'] == 'done'
    assert proc['order']['request']['corp']['user_id'] == 'user_id'
    assert proc['order']['request']['corp']['client_id'] == '12345'


PRICING_DATA = {
    'driver': {
        'category_id': '8e94ac99f32148ef8a4512c95c76d605',
        'tariff_id': '01234567890abcdefghij0987654321z',
        'additional_prices': {},
        'trip_information': {
            'distance': 11469.067742347717,
            'jams': True,
            'time': 970,
        },
        'base_price': {
            'boarding': 100,
            'destination_waiting': 0,
            'distance': 94.22160968112945,
            'requirements': 0,
            'time': 164.83333333333331,
            'transit_waiting': 0,
            'waiting': 0,
        },
        'category_prices_id': 'c/8e94ac99f32148ef8a4512c95c76d605',
        'meta': {},
        'modifications': {
            'for_fixed': [358, 352, 482, 526, 534],
            'for_taximeter': [358, 352, 482, 526, 534],
        },
        'price': {'total': 719.0},
    },
    'fixed_price': True,
    'geoarea_ids': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    'currency': {'fraction_digits': 0, 'name': 'RUB', 'symbol': '₽'},
    'tariff_info': {
        'time': {'included_minutes': 0, 'price_per_minute': 0},
        'distance': {'included_kilometers': 0, 'price_per_kilometer': 0},
        'max_free_waiting_time': 2,
        'point_a_free_waiting_time': 1,
    },
    'taximeter_metadata': {'show_price_in_taximeter': False},
    'trip_information': {
        'distance': 11469.067742347717,
        'jams': True,
        'time': 970,
    },
    'user': {
        'category_id': '8e94ac99f32148ef8a4512c95c76d605',
        'tariff_id': '01234567890abcdefghij0987654321z',
        'additional_prices': {},
        'trip_information': {
            'distance': 11469.067742347717,
            'jams': True,
            'time': 970,
        },
        'base_price': {
            'boarding': 100,
            'destination_waiting': 0,
            'distance': 94.22160968112945,
            'requirements': 0,
            'time': 164.83333333333331,
            'transit_waiting': 0,
            'waiting': 0,
        },
        'category_prices_id': 'c/8e94ac99f32148ef8a4512c95c76d605',
        'data': {
            'category_data': {
                'corp_decoupling': False,
                'decoupling': False,
                'fixed_price': True,
            },
        },
        'meta': {},
        'modifications': {
            'for_fixed': [358, 352, 482, 526, 498, 534, 540],
            'for_taximeter': [358, 352, 482, 526, 498, 534, 540],
        },
        'price': {'total': 503.0, 'strikeout': 719.0},
    },
}


@pytest.mark.parametrize(
    'order_id,exp_svc_request,exp_fixed_price,exp_calc_info,exp_classes,'
    'exp_user_total_price, error_response',
    [
        (
            'multiclass_simple',
            {
                'common': {
                    'destination': [37.5, 55.7],
                    'max_distance_from_b': 500.0,
                    'show_price_in_taximeter': False,
                },
                'id': 'multiclass_simple',
                'prices_info': [
                    {
                        'class': 'econom',
                        'prices': {'price': 250.0, 'price_original': 250.0},
                        'surge': {'value': 2.5},
                    },
                    {
                        'class': 'business',
                        'prices': {'price': 200.0, 'price_original': 200.0},
                        'surge': {'value': 1.0},
                    },
                ],
            },
            {
                'destination': [37.5, 55.7],
                'max_distance_from_b': 500,
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
            },
            {
                'allowed_tariffs': {
                    '__park__': {'business': 200.0, 'econom': 100.0},
                },
                'distance': 5000.0,
                'recalculated': False,
                'time': 123.0,
            },
            ['econom', 'business'],
            250.0,  # by fixed price
            None,
        ),
        (
            'multiclass_with_only_business',
            None,  # no request because there is only 1 class
            {
                'destination': [37.5, 55.7],
                'max_distance_from_b': 500,
                'price': 200.0,
                'price_original': 200.0,
                'show_price_in_taximeter': False,
            },
            {
                'allowed_tariffs': {
                    '__park__': {'business': 200.0, 'econom': 100.0},
                },
                'distance': 5000.0,
                'recalculated': False,
                'time': 123.0,
            },
            ['business'],
            200.0,  # by fixed price
            None,
        ),
        (
            'multiclass_without_destination',
            {
                'id': 'multiclass_without_destination',
                'prices_info': [
                    {'class': 'econom', 'surge': {'value': 1.2}},
                    {'class': 'business', 'surge': {'value': 1.0}},
                ],  # no request because there is no destination
            },
            None,  # no fixed price without destination
            {
                'allowed_tariffs': {
                    '__park__': {'business': 199.0, 'econom': 99.0},
                },
                'distance': 0.0,
                'recalculated': True,
                'time': 0.0,
            },
            ['econom', 'business'],
            119.0,  # calc econom with surge
            None,
        ),
        (
            'multiclass_simple_decoupling',
            {
                'common': {
                    'destination': [37.5, 55.7],
                    'max_distance_from_b': 500.0,
                    'show_price_in_taximeter': False,
                },
                'id': 'multiclass_simple_decoupling',
                'prices_info': [
                    {
                        'class': 'econom',
                        'prices': {'price': 250.0, 'price_original': 250.0},
                        'surge': {'value': 2.5},
                        'decoupling': {
                            'driver_price_info': {
                                'category_id': (
                                    'b7c4d5f6aa3b40a3807bb74b3bc042af'
                                ),
                                'fixed_price': 317.0,
                                'sp': 1.0,
                                'sp_alpha': 1.0,
                                'sp_beta': 0.0,
                                'sp_surcharge': 0.0,
                                'tariff_id': '585a6f47201dd1b2017a0eab',
                            },
                            'user_price_info': {
                                'category_id': (
                                    '5f40b7f324414f51a1f9549c65211ea5'
                                ),
                                'fixed_price': 633.0,
                                'sp': 1.0,
                                'sp_alpha': 1.0,
                                'sp_beta': 0.0,
                                'sp_surcharge': 0.0,
                                'tariff_id': (
                                    '585a6f47201dd1b2017a0eab'
                                    '-507000939f17427e951df9791573ac7e'
                                    '-7fc5b2d1115d4341b7be206875c40e11'
                                ),
                            },
                        },
                    },
                    {
                        'class': 'business',
                        'prices': {'price': 199.0, 'price_original': 199.0},
                        'surge': {'value': 1.0},
                        'decoupling': {
                            'driver_price_info': {
                                'category_id': (
                                    '852f208027fb4c2eb944148e16fa5db1'
                                ),
                                'fixed_price': 556.0,
                                'sp': 1.0,
                                'sp_alpha': 0.2,
                                'sp_beta': 0.8,
                                'sp_surcharge': 0.0,
                                'tariff_id': '585a6f47201dd1b2017a0eab',
                            },
                            'user_price_info': {
                                'category_id': (
                                    '21cbf8c5887b464e93bb5718033e08c7'
                                ),
                                'fixed_price': 15775.0,
                                'sp': 1.0,
                                'sp_alpha': 0.2,
                                'sp_beta': 0.8,
                                'sp_surcharge': 0.0,
                                'tariff_id': (
                                    '585a6f47201dd1b2017a0eab'
                                    '-507000939f17427e951df9791573ac7e'
                                    '-7fc5b2d1115d4341b7be206875c40e11'
                                ),
                            },
                        },
                    },
                ],
            },
            {
                'destination': [37.5, 55.7],
                'max_distance_from_b': 500,
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
            },
            {
                'allowed_tariffs': {
                    '__park__': {'business': 199.0, 'econom': 100.0},
                },
                'distance': 5000.0,
                'recalculated': False,
                'time': 123.0,
            },
            ['econom', 'business'],
            250.0,  # by fixed price
            None,
        ),
        (
            'multiclass_simple_with_new_pricing_data',
            {
                'common': {
                    'destination': [37.5, 55.7],
                    'show_price_in_taximeter': False,
                },
                'id': 'multiclass_simple_with_new_pricing_data',
                'prices_info': [
                    {
                        'class': 'econom',
                        'prices': {'price': 250.0, 'price_original': 250.0},
                        'surge': {'value': 2.5},
                        'pricing_data': PRICING_DATA,
                        'current_prices': {
                            'kind': 'fixed',
                            'user_ride_display_price': 250.0,
                            'user_total_display_price': 250.0,
                            'user_total_price': 250.0,
                        },
                    },
                    {
                        'class': 'business',
                        'prices': {'price': 200.0, 'price_original': 200.0},
                        'surge': {'value': 1.0},
                        'pricing_data': PRICING_DATA,
                        'current_prices': {
                            'kind': 'fixed',
                            'user_ride_display_price': 200.0,
                            'user_total_display_price': 200.0,
                            'user_total_price': 200.0,
                        },
                    },
                ],
            },
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
            },
            {
                'allowed_tariffs': {
                    '__park__': {'business': 200.0, 'econom': 100.0},
                },
                'distance': 5000.0,
                'recalculated': False,
                'time': 123.0,
            },
            ['econom', 'business'],
            250.0,  # by fixed price
            None,
        ),
        (
            'multiclass_simple_with_paid_supply_classes',
            {
                'common': {
                    'destination': [37.5, 55.7],
                    'show_price_in_taximeter': False,
                },
                'id': 'multiclass_simple_with_paid_supply_classes',
                'prices_info': [
                    {
                        'class': 'econom',
                        'prices': {
                            'paid_supply_price': 130.0,
                            'price': 250.0,
                            'price_original': 250.0,
                        },
                        'surge': {'value': 2.5},
                        'pricing_data': PRICING_DATA,
                        'current_prices': {
                            'kind': 'fixed',
                            'user_ride_display_price': 250.0,
                            'user_total_display_price': 250.0,
                            'user_total_price': 250.0,
                        },
                    },
                    {
                        'class': 'business',
                        'prices': {'price': 200.0, 'price_original': 200.0},
                        'surge': {'value': 1.0},
                        'pricing_data': PRICING_DATA,
                        'current_prices': {
                            'kind': 'fixed',
                            'user_ride_display_price': 200.0,
                            'user_total_display_price': 200.0,
                            'user_total_price': 200.0,
                        },
                    },
                    {
                        'class': 'vip',
                        'prices': {
                            'paid_supply_price': 130.0,
                            'price': 500.0,
                            'price_original': 500.0,
                        },
                        'surge': {'value': 1.0},
                        'pricing_data': PRICING_DATA,
                        'current_prices': {
                            'kind': 'fixed',
                            'user_ride_display_price': 500.0,
                            'user_total_display_price': 500.0,
                            'user_total_price': 500.0,
                        },
                    },
                ],
            },
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
                'paid_supply_price': 130,
            },
            {
                'allowed_tariffs': {
                    '__park__': {
                        'business': 200.0,
                        'econom': 100.0,
                        'vip': 500.0,
                    },
                },
                'distance': 5000.0,
                'recalculated': False,
                'time': 123.0,
            },
            ['econom', 'business', 'vip'],
            250.0,  # by fixed price
            None,
        ),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.parametrize('with_due', [True, False])
@pytest.mark.parametrize('emulate_svc_failure', (False, True))
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge', 'fixed_price')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    ORDER_COMMIT_CURRENT_PRICES_IN_MULTICLASS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'multiclass-pricing-storage'}],
    TVM_SERVICES={'multiclass-pricing-storage': 24},
)
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_ordercommit_multiclass(
        taxi_protocol,
        db,
        ordercommit_services,
        order_id,
        exp_svc_request,
        exp_fixed_price,
        exp_calc_info,
        exp_classes,
        exp_user_total_price,
        emulate_svc_failure,
        error_response,
        tvm2_client,
        mockserver,
        with_due,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_user_surge(sp=1.2, category='econom')
    pricing_data_preparer.set_driver_surge(sp=1.2, category='econom')
    pricing_data_preparer.set_cost(118.8, 118.8, 'econom')
    pricing_data_preparer.set_cost(199.0, 199.0, 'business')
    pricing_data_preparer.set_trip_information(0.0, 0.0)

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/multiclass_pricing_storage/v1/prices/add')
    def add_multiclass_price(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        tvm_ticket = request.headers['X-Ya-Service-Ticket']
        assert tvm_ticket == ticket

        expected_request = (
            ordercommit_services.multiclass_pricing_storage_expected_request
        )
        if expected_request is not None:
            data = json.loads(request.get_data())
            if order_id == 'multiclass_without_destination':
                assert 'prices_info' in data
                for price_info in data['prices_info']:
                    assert 'pricing_data' in price_info
                    del price_info['pricing_data']
                    del price_info['current_prices']
            elif order_id not in (
                'multiclass_simple_with_new_pricing_data',
                'multiclass_simple_with_paid_supply_classes',
            ):
                for price_info in data['prices_info']:
                    del price_info['pricing_data']
                    del price_info['current_prices']
            assert data == expected_request
        ordercommit_services.multiclass_pricing_storage_request_got = True
        if ordercommit_services.multiclass_pricing_storage_emulate_failure:
            return mockserver.make_response('', 500)
        return ordercommit_services.multiclass_pricing_storage_response

    expected_request = deepcopy(exp_svc_request)
    if with_due and expected_request:
        expected_request['due'] = '2017-07-19T17:16:55+00:00'
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='multiclass_preorder_due',
            consumers=['protocol/ordercommit'],
            clauses=[
                {
                    'title': '',
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                },
            ],
        )
    ordercommit_services.multiclass_pricing_storage_expected_request = (
        expected_request
    )
    ordercommit_services.payment_type = 'personal_wallet'
    ordercommit_services.surge_tariff_classes = exp_classes
    ordercommit_services.experiments = ['forced_surge', 'fixed_price']

    # check that everything works ok even if the multiclass service fails
    ordercommit_services.multiclass_pricing_storage_emulate_failure = (
        emulate_svc_failure
    )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )

    if error_response:
        assert response.status_code == error_response['status']
        assert response.json() == error_response['body']
        return

    assert response.status_code == 200

    assert ordercommit_services.multiclass_pricing_storage_request_got == (
        exp_svc_request is not None
    )

    proc = db.order_proc.find_one({'_id': order_id})
    order = proc['order']
    request = order['request']
    assert request['class'] == exp_classes
    assert order.get('fixed_price') == exp_fixed_price
    assert order['calc'] == exp_calc_info
    if len(exp_classes) > 1:
        if order_id == 'multiclass_simple_with_paid_supply_classes':
            assert proc['extra_data']['multiclass']['paid_supply_classes'] == [
                'econom',
                'vip',
            ]
        else:
            assert (
                proc['extra_data']['multiclass']['paid_supply_classes'] == []
            )
    exp_kind = 'fixed' if exp_fixed_price else 'prediction'
    order_commit_common.check_current_prices(
        proc, exp_kind, exp_user_total_price,
    )


@pytest.mark.parametrize(
    'exp_order_proc_fixed_price,offer_paid_supply_data,config_enabled',
    [
        (
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
                'paid_supply_price': 130,
            },
            {},
            False,
        ),
        (
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
                'paid_supply_price': 130,
                'paid_supply_info': {'time': 1, 'distance': 2},
            },
            {
                'econom': {'paid_supply_info': {'time': 1, 'distance': 2}},
                'vip': {'paid_supply_info': {'time': 3, 'distance': 4}},
            },
            False,
        ),
        (
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
                'paid_supply_price': 130,
                'paid_supply_info': {'time': 3, 'distance': 4},
            },
            {
                'econom': {'paid_supply_info': {'time': 1, 'distance': 2}},
                'vip': {'paid_supply_info': {'time': 3, 'distance': 4}},
            },
            True,
        ),
        (
            {
                'destination': [37.5, 55.7],
                'price': 250.0,
                'price_original': 250.0,
                'show_price_in_taximeter': False,
                'paid_supply_price': 130,
                'paid_supply_info': {'time': 5, 'distance': 4},
            },
            {
                'econom': {'paid_supply_info': {'time': 5, 'distance': 2}},
                'vip': {'paid_supply_info': {'time': 3, 'distance': 4}},
            },
            True,
        ),
    ],
    ids=[
        'no_paid_supply_info',
        'disabled_config',
        'enabled_config',
        'enabled_config_from_different_classes',
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge', 'fixed_price')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True,
    ORDER_COMMIT_CURRENT_PRICES_IN_MULTICLASS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'multiclass-pricing-storage'}],
    TVM_SERVICES={'multiclass-pricing-storage': 24},
)
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_ordercommit_multiclass_paid_supply(
        taxi_protocol,
        db,
        ordercommit_services,
        exp_order_proc_fixed_price,
        tvm2_client,
        mockserver,
        experiments3,
        pricing_data_preparer,
        offer_paid_supply_data,
        config_enabled,
        load_json,
):
    offer_id = 'offer_multiclass_simple_with_paid_supply_classes'
    order_id = 'multiclass_simple_with_paid_supply_classes'
    exp_classes = ['econom', 'business', 'vip']
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_user_surge(sp=1.2, category='econom')
    pricing_data_preparer.set_driver_surge(sp=1.2, category='econom')
    pricing_data_preparer.set_cost(118.8, 118.8, 'econom')
    pricing_data_preparer.set_cost(199.0, 199.0, 'business')
    pricing_data_preparer.set_trip_information(0.0, 0.0)

    config = load_json('experiments3_multiclass_paid_supply_settings.json')
    config['configs'][0]['match']['enabled'] = config_enabled
    experiments3.add_experiments_json(config)

    for category, data in offer_paid_supply_data.items():
        update_data = {
            'prices.$[element].' + key: value for key, value in data.items()
        }
        if update_data:
            update_result = db.order_offers.update_many(
                {'_id': offer_id},
                {'$set': update_data},
                array_filters=[{'element.cls': category}],
            )
            assert update_result.modified_count == 1

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/multiclass_pricing_storage/v1/prices/add')
    def add_multiclass_price(request):
        ordercommit_services.multiclass_pricing_storage_request_got = True
        return ordercommit_services.multiclass_pricing_storage_response

    ordercommit_services.payment_type = 'personal_wallet'
    ordercommit_services.surge_tariff_classes = exp_classes
    ordercommit_services.experiments = ['forced_surge', 'fixed_price']

    # check that everything works ok even if the multiclass service fails
    ordercommit_services.multiclass_pricing_storage_emulate_failure = False

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )

    assert response.status_code == 200
    assert ordercommit_services.multiclass_pricing_storage_request_got

    proc = db.order_proc.find_one({'_id': order_id})
    order = proc['order']
    assert order.get('fixed_price') == exp_order_proc_fixed_price


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments('coop_account')
@pytest.mark.config(
    COMMIT_PLUGINS_ENABLED=True, COOP_ACCOUNT_CHECK_AVAILABLE=True,
)
@pytest.mark.parametrize(
    'can_make_order',
    ['true', 'false_without_reason', 'false_with_reason', 'not_exists'],
)
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_ordercommit_coop_account_available(
        taxi_protocol,
        mockserver,
        cardstorage,
        ordercommit_services,
        can_make_order,
):
    @mockserver.json_handler(
        '/coop_account/internal/coop_account/check_available',
    )
    def available(request):
        query_string = (
            'account_id=coop_account_id&'
            'cost=250&'
            'locale=ru&'
            'phone_id=5714f45e98956f06baaae3d4&'
            'yandex_uid=4003514353'
        )
        assert query_string == request.query_string.decode()

        if can_make_order == 'not_exists':
            return {
                'code': 'GENERAL',
                'system_message': 'account does not exist',
            }
        if can_make_order == 'false_with_reason':
            return {
                'available': False,
                'reason': 'Превышен лимит по семейной карте',
            }
        if can_make_order == 'false_without_reason':
            return {'available': False}

        return {'available': True}

    response = taxi_protocol.post(
        '3.0/ordercommit',
        json={'id': USER_ID, 'orderid': 'order_coop_account'},
    )
    resp_json = response.json()

    if can_make_order == 'true':
        assert response.status_code == 200
        assert resp_json['orderid'] == 'order_coop_account'
        assert resp_json['status'] == 'search'
    else:
        assert response.status_code == 406
        assert resp_json['error']['code'] == 'COOP_ACCOUNT_UNAVAILABLE'
        if can_make_order == 'false_with_reason':
            assert (
                resp_json['error']['text']
                == 'Превышен лимит по семейной карте'
            )


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.parametrize(
    'paymentmethod_response_code, paymentmethod_response_body',
    [
        pytest.param(
            200,
            {
                'owner_uid': '4006736929',
                'type': 'card',
                'payment_method_id': 'card-x5619',
                'billing_id': 'x5619',
                'persistent_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            },
            id='paymentmethod_success',
        ),
        pytest.param(
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'details': {},
                'system_message': 'account coop_account_id does not exist',
            },
            id='paymentmethod_not_found',
        ),
        pytest.param(500, None, id='paymentmethod_error'),
    ],
)
def test_ordercommit_coop_account_paymentmethod(
        taxi_protocol,
        mockserver,
        paymentmethod_response_code,
        paymentmethod_response_body,
):
    @mockserver.json_handler(
        '/coop_account/internal/coop_account/paymentmethod',
    )
    def paymentmethod(request):
        expected_query = 'account_id=coop_account_id&yandex_uid=4003514353'
        assert request.query_string.decode() == expected_query
        return mockserver.make_response(
            json.dumps(paymentmethod_response_body),
            paymentmethod_response_code,
        )

    response = taxi_protocol.post(
        '3.0/ordercommit',
        json={'id': USER_ID, 'orderid': 'order_coop_account'},
    )
    resp_json = response.json()

    if paymentmethod_response_code == 404:
        assert response.status_code == 406
        assert resp_json['error']['code'] == 'COOP_ACCOUNT_UNAVAILABLE'
    else:
        assert response.status_code == 200
        assert resp_json['orderid'] == 'order_coop_account'
        assert resp_json['status'] == 'search'


@pytest.mark.filldb(order_proc='pending')
def test_ordercommit_sbp(taxi_protocol, pricing_data_preparer):
    pricing_data_preparer.set_locale('ru')
    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': 'order_sbp'},
    )
    response_body = response.json()

    assert response.status_code == 200
    assert response_body['orderid'] == 'order_sbp'
    assert response_body['status'] == 'search'


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.translations(
    client_messages={
        'shared_payments.family_card_limit_reached': {
            'ru': 'недостаточно денег на семейной карте',
        },
    },
)
@pytest.mark.parametrize(
    'currency, available, is_ok',
    [
        # price=100 ok (max_order_price = 250)
        ('RUB', 250, True),
        # price above limit
        ('RUB', 50, False),
        # currency mismatch -- call currency/convert
        ('USD', 50, True),
    ],
)
def test_ordercommit_family_card_limits(
        taxi_protocol,
        mockserver,
        cardstorage,
        ordercommit_services,
        mongodb,
        currency,
        available,
        is_ok,
):
    @mockserver.json_handler('/antifraud/v1/currency/convert')
    def mock_afs_currency_convert(request):
        data = json.loads(request.get_data())
        assert data == {
            'currency_from': 'USD',
            'currency_to': 'RUB',
            'value': 50,
        }
        return {'value': 3000}

    family_limit = 50000
    family_expenses = family_limit - 100 * available
    mongodb.cards.update_one(
        {'owner_uid': '4003514353', 'payment_id': 'card-x5618'},
        {
            '$set': {
                'payer_info.family_info.limit': family_limit,
                'payer_info.family_info.expenses': family_expenses,
                'payer_info.family_info.currency': currency,
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/ordercommit',
        json={'id': USER_ID, 'orderid': 'order_family_card'},
    )
    resp_json = response.json()

    if is_ok:
        assert response.status_code == 200
        assert resp_json['orderid'] == 'order_family_card'
        assert resp_json['status'] == 'search'
    else:
        assert response.status_code == 406
        assert resp_json['error']['code'] == 'COOP_ACCOUNT_UNAVAILABLE'
        assert (
            resp_json['error']['text']
            == 'недостаточно денег на семейной карте'
        )

    if currency == 'USD':
        assert mock_afs_currency_convert.has_calls
    else:
        assert not mock_afs_currency_convert.has_calls

    # check order_proc.payment_tech.family
    order_doc = mongodb.order_proc.find_one({'_id': 'order_family_card'})
    if is_ok:
        assert order_doc['payment_tech']['family'] == {
            'is_owner': False,
            'limit': family_limit,
            'expenses': family_expenses,
            'currency': currency,
            'frame': 'month',
            'owner_uid': '111122223333',
        }
    else:
        assert 'family' not in order_doc['payment_tech']


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
@pytest.mark.parametrize('order_id', ['surge_12'])
def test_pass_locale(
        taxi_protocol, ordercommit_services, mockserver, mongodb, order_id,
):
    order_doc = mongodb.order_proc.find_one({'_id': order_id})
    assert order_doc
    assert 'order' in order_doc
    assert 'user_locale' in order_doc['order']
    locale = order_doc['order']['user_locale']

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        request_json = json.loads(request.get_data())
        assert 'zone' in request_json and request_json['zone']
        assert request.headers['Accept-Language'] == locale
        return {}

    taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )
    assert _mock_v2_prepare.has_calls


SMART_PRICING_FALLBACK_SETTINGS_ENABLED = {
    'enabled': True,
    'forced_enabled': True,
}
SMART_PRICING_FALLBACK_SETTINGS_DISABLED = {
    'enabled': False,
    'forced_enabled': False,
}


@pytest.mark.parametrize(
    'forced_use_pricing_fallback_enabled',
    [False, True],
    ids=[
        'forced_use_pricing_fallback_disabled',
        'forced_use_pricing_fallback_enabled',
    ],
)
@pytest.mark.parametrize(
    'pricing_fallback_enabled',
    [False, True],
    ids=['pricing_fallback_disabled', 'pricing_fallback_enabled'],
)
@pytest.mark.parametrize(
    'pdp_response_result',
    [False, True],
    ids=['pdp_bad_response', 'pdp_good_response'],
)
@pytest.mark.parametrize(
    'pricing_fallback_response_result',
    [False, True],
    ids=['pricing_fallback_bad_response', 'pricing_fallback_good_response'],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_pricing_fallback(
        taxi_protocol,
        experiments3,
        ordercommit_services,
        pricing_fallback_enabled,
        forced_use_pricing_fallback_enabled,
        pdp_response_result,
        pricing_fallback_response_result,
        mockserver,
        load_json,
        config,
        db,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_pricing_data_preparer(request):
        if not pdp_response_result:
            return mockserver.make_response('', 500)
        return load_json('pdp_v2_prepare_response.json')

    @mockserver.json_handler('/pricing_fallback/v1/get_pricing_data')
    def mock_pricing_fallback(request):
        if not pricing_fallback_response_result:
            return mockserver.make_response('', 500)
        return load_json('pricing_fallback_get_pricing_data_response.json')

    order_id = 'surge_12'
    config.set_values(
        dict(
            SMART_PRICING_FALLBACK_SETTINGS=(
                SMART_PRICING_FALLBACK_SETTINGS_ENABLED
                if pricing_fallback_enabled
                else SMART_PRICING_FALLBACK_SETTINGS_DISABLED
            ),
        ),
    )
    ordercommit_services.experiments = ['fixed_price']

    if forced_use_pricing_fallback_enabled:
        experiments3.add_experiments_json(
            load_json('experiments3_forced_use_pricing_fallback.json'),
        )

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': order_id},
    )

    assert mock_pricing_data_preparer.has_calls
    assert mock_pricing_fallback.has_calls == (
        pricing_fallback_enabled or forced_use_pricing_fallback_enabled
    )
    assert mock_pricing_data_preparer.times_called == (
        1 if (pdp_response_result or pricing_fallback_enabled) else 3
    )

    if (
            pdp_response_result
            or (pricing_fallback_enabled and pricing_fallback_response_result)
            or (
                forced_use_pricing_fallback_enabled
                and pricing_fallback_response_result
            )
    ):
        assert response.status_code == 200
        proc = db.order_proc.find_one({'_id': order_id})
        assert proc and 'order' in proc
        if not pdp_response_result:
            assert 'fixed_price' not in proc['order']
            assert (
                proc['order'].get('fixed_price_discard_reason', None)
                == 'is_pricing_fallback'
            )
    else:
        assert response.status_code == 500


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize(
    (
        'pdp_response_code',
        'pricing_fallback_enabled',
        'ordercommit_response_code',
    ),
    [
        pytest.param(200, False, 200, id='pdp_code_200'),
        pytest.param(400, False, 500, id='pdp_code_400'),
        pytest.param(429, False, 500, id='pdp_code_429'),
        pytest.param(500, False, 500, id='pdp_code_500'),
        pytest.param(400, True, 200, id='pdp_code_400_fallback'),
        pytest.param(429, True, 200, id='pdp_code_429_fallback'),
        pytest.param(500, True, 200, id='pdp_code_500_fallback'),
    ],
)
def test_pdp_response_code(
        ordercommit_services,
        taxi_protocol,
        mockserver,
        load_json,
        pdp_response_code,
        ordercommit_response_code,
        pricing_fallback_enabled,
        config,
):
    config.set_values(
        dict(
            SMART_PRICING_FALLBACK_SETTINGS=(
                SMART_PRICING_FALLBACK_SETTINGS_ENABLED
                if pricing_fallback_enabled
                else SMART_PRICING_FALLBACK_SETTINGS_DISABLED
            ),
        ),
    )

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        if pdp_response_code == 400:
            response_json = {
                'message': 'error UNABLE_TO_MATCH_TARIFF',
                'code': 'UNABLE_TO_MATCH_TARIFF',
            }
            return mockserver.make_response(json.dumps(response_json), 400)
        elif pdp_response_code != 200:
            return mockserver.make_response({}, pdp_response_code)
        return load_json('pdp_response.json')

    @mockserver.json_handler('/pricing_fallback/v1/get_pricing_data')
    def mock_pricing_fallback(request):
        return load_json('pricing_fallback_get_pricing_data_response.json')

    ordercommit_services.experiments = ['fixed_price']

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': 'surge_12'},
    )

    assert response.status_code == ordercommit_response_code
