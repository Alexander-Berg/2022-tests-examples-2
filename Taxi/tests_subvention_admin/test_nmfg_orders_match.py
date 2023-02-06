import collections

import bson
import pytest


Validator = collections.namedtuple('Validator', ['is_satisfied', 'value'])


@pytest.fixture(name='mock_v1_retrieve_by_uniques')
def _mock_v1_retrieve_by_uniques(mockserver, load_json):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    async def handler(request):
        return load_json('driver_profiles_retrieve_by_uniques_response.json')

    return handler


@pytest.fixture(name='mock_v1_parks_orders_list')
def _mock_v1_parks_orders_list(mockserver, load_json):
    class Context:
        def __init__(self) -> None:
            self.context = load_json('do_parks_orders_list.json')
            self.handler = None

        def set_field(self, idx, key, value):
            self.context['orders'][idx][key] = value

    ctx = Context()

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def handler(request):
        return ctx.context

    ctx.handler = handler

    return ctx


@pytest.fixture(name='mock_bs_v1_rules_select')
def _mock_bs_v1_rules_select(mockserver, load_json):
    class Context:
        def __init__(self) -> None:
            self.context = load_json('bs_rules_select_response.json')
            self.handler = None

        def set_field(self, idx, key, value):
            self.context[idx][key] = value

    ctx = Context()

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def handler(request):
        return {'subventions': ctx.context}

    ctx.handler = handler

    return ctx


@pytest.fixture(name='mock_bsx_v1_rules_match')
def _mock_bsx_v1_rules_match(mockserver, load_json):
    @mockserver.json_handler('billing-subventions-x/v1/rules/match')
    async def handler(request):
        handler.req = request

        req = request.json

        rule = load_json('bsx_rules_match.json')[0]

        if (
                req['activity_points'] >= rule['activity_points']
                and req['tariff_class'] in rule['tariff_class']
                and req['zone_name'] == rule['zone_name']
                and set(req['tags']) & set(rule['tags']) != {}
                and req['driver_branding'] == rule['branding_type']
        ):
            return {'match': [rule]}

        return {'match': []}

    return handler


@pytest.fixture(name='mock_soc_v1_context')
def _mock_soc_v1_context(mockserver, load_json):
    class Context:
        def __init__(self) -> None:
            self.context = load_json('soc_context_response.json')
            self.handler = None

        def set_field(self, key, value):
            self.context[key] = value

    ctx = Context()

    @mockserver.json_handler(
        '/subvention-order-context/internal'
        '/subvention-order-context/v1/context',
    )
    async def handler():
        return ctx.context

    ctx.handler = handler

    return ctx


@pytest.fixture(name='mock_oa_v1_order_proc_retrieve')
def _mock_oa_v1_order_proc_retrieve(mockserver):
    class Context:
        def __init__(self) -> None:
            self.context = {
                '_id': 'real_id',
                'order': {'pricing_data': {'currency': {'name': 'RUB'}}},
            }
            self.handler = None

        def set_doc(self, doc) -> None:
            self.context = doc

        def set_field(self, key, value):
            self.context[key] = value

    ctx = Context()

    @mockserver.handler('order-archive/v1/order_proc/retrieve')
    async def handler(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({'doc': ctx.context}),
        )

    ctx.handler = handler

    return ctx


@pytest.fixture(name='mock_driver_mode_index_v1_mode_history')
def _mock_driver_mode_index_v1_mode_history(mockserver, load_json):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    async def handler(request):
        assert request.json['begin_at'] == '1970-01-01T00:00:00+00:00'

        handler.req = request
        return {
            'docs': [
                {
                    'external_event_ref': 'mock_event_ref',
                    'event_at': '2021-09-23T08:37:49.370176+00:00',
                    'data': {
                        'driver': {
                            'park_id': 'mock_park_id',
                            'driver_profile_id': 'mock_driver_id',
                        },
                        'mode': 'lavka_couriers_pedestrian',
                        'subscription_data': {
                            'source': 'service_mode_reset',
                            'reason': 'import_profile',
                        },
                    },
                },
            ],
            'cursor': '',
        }

    return handler


@pytest.mark.parametrize(
    'context_updates,validators',
    [
        pytest.param(
            # context_updates
            {
                # Default rule
                # Default context
                # Default order
                # Default order_proc
                # Default response
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'activity': Validator(True, 100),
                'tariff': Validator(True, 'econom'),
                'tariff_zone': Validator(True, 'moscow'),
                'order_status': Validator(True, 'complete'),
                'NMFG_tag': Validator(True, True),
                'reposition_enabled': Validator(True, False),
                'branding': Validator(True, None),
                'price_changed': Validator(True, False),
            },
            id='Everything is satisfied',
        ),
        pytest.param(
            # context_updates
            {
                'soc_context': {
                    'activity_points': 86,
                    'tariff_class': 'business',
                    'tariff_zone': 'perm',
                    'tags': ['reposition_district'],
                    'branding': {'has_lightbox': False, 'has_sticker': False},
                },
                'response': {
                    'satisfied': False,
                    'included_in_quantity': False,
                    'included_in_income': False,
                },
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'activity': Validator(False, 86),
                'tariff': Validator(False, 'business'),
                'tariff_zone': Validator(False, 'perm'),
                'order_status': Validator(True, 'complete'),
                'NMFG_tag': Validator(False, False),
                'reposition_enabled': Validator(False, True),
                'branding': Validator(False, None),
                'price_changed': Validator(True, False),
            },
            id='Everything but date fails',
        ),
        pytest.param(
            # context_updates
            {
                'rule': {
                    'min_activity_points': None,
                    'tariff_classes': None,
                    'branding_type': None,
                },
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'tariff_zone': Validator(True, 'moscow'),
                'order_status': Validator(True, 'complete'),
                'NMFG_tag': Validator(True, True),
                'reposition_enabled': Validator(True, False),
                'price_changed': Validator(True, False),
            },
            id='All optional properties omitted',
        ),
        pytest.param(
            # context_updates
            {
                'order': {'status': 'cancelled'},
                'response': {
                    'satisfied': False,
                    'included_in_quantity': False,
                },
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'activity': Validator(True, 100),
                'tariff': Validator(True, 'econom'),
                'tariff_zone': Validator(True, 'moscow'),
                'order_status': Validator(False, 'cancelled'),
                'NMFG_tag': Validator(True, True),
                'reposition_enabled': Validator(True, False),
                'branding': Validator(True, None),
                'price_changed': Validator(True, False),
            },
            id='Order status is not satisfied',
        ),
        pytest.param(
            # context_updates
            {
                'order_proc': {
                    'order': {
                        'pricing_data': {'currency': {'name': 'RUB'}},
                        'disp_cost': {'disp_cost': 100},
                    },
                },
                'response': {'satisfied': False, 'included_in_income': False},
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'activity': Validator(True, 100),
                'tariff': Validator(True, 'econom'),
                'tariff_zone': Validator(True, 'moscow'),
                'order_status': Validator(True, 'complete'),
                'NMFG_tag': Validator(True, True),
                'reposition_enabled': Validator(True, False),
                'branding': Validator(True, None),
                'price_changed': Validator(False, True),
            },
            id='Price is changed by a dispatcher',
        ),
        pytest.param(
            # context_updates
            {
                'soc_context': {'tags': ['subv_disable_nmfg']},
                'response': {
                    'disabled_by_tags': True,
                    'satisfied': False,
                    'included_in_quantity': False,
                    'included_in_income': False,
                },
            },
            # validators
            {
                'date': Validator(True, '2022-04-07T08:57:09.274+00:00'),
                'activity': Validator(True, 100),
                'tariff': Validator(True, 'econom'),
                'tariff_zone': Validator(True, 'moscow'),
                'order_status': Validator(True, 'complete'),
                'NMFG_tag': Validator(False, False),
                'reposition_enabled': Validator(True, False),
                'branding': Validator(True, None),
                'price_changed': Validator(True, False),
            },
            id='Tags contain a disabling tag',
        ),
    ],
)
async def test_nmfg_orders_match(
        taxi_subvention_admin,
        mock_v1_retrieve_by_uniques,
        mock_v1_parks_orders_list,
        mock_bs_v1_rules_select,
        mock_bsx_v1_rules_match,
        mock_soc_v1_context,
        mock_oa_v1_order_proc_retrieve,
        mock_driver_mode_index_v1_mode_history,
        context_updates,
        mockserver,
        validators,
):
    def context_updates_items(key: str) -> dict:
        if key in context_updates:
            return context_updates[key].items()

        return {}

    for key, value in context_updates_items('rule'):
        mock_bs_v1_rules_select.set_field(0, key, value)

    for key, value in context_updates_items('soc_context'):
        mock_soc_v1_context.set_field(key, value)

    for key, value in context_updates_items('order'):
        mock_v1_parks_orders_list.set_field(0, key, value)

    ref_response = {
        'satisfied': True,
        'order_id': 'real_id',
        'income': 50.0,
        'currency': 'RUB',
        'driver_mode': 'lavka_couriers_pedestrian',
        'disabled_by_tags': False,
        'included_in_income': True,
        'included_in_quantity': True,
    }

    for key, value in context_updates_items('response'):
        ref_response[key] = value

    if 'order_proc' in context_updates:
        for key, value in context_updates['order_proc'].items():
            mock_oa_v1_order_proc_retrieve.set_field(key, value)

    response = await taxi_subvention_admin.post(
        '/internal/subvention-admin/v1/nmfg/orders/match',
        json={
            'unique_driver_id': 'mock_udid',
            'time_range': {
                'start': '2022-03-01T00:00:00Z',
                'end': '2022-03-15T00:00:00Z',
            },
            'rule_id': '4358d289-ac0b-4c66-acfb-802620392bb2',
        },
    )

    assert response.status_code == 200

    orders = response.json()['orders']

    assert len(orders) == 1

    order = orders[0]

    assert len(order['properties']) == len(validators)

    for prop in order['properties']:
        validator = validators[prop['type']]

        if validator.is_satisfied is not None:
            assert validator.is_satisfied == prop['is_satisfied']

        if validator.value is not None:
            assert validator.value == prop['value']

    order.pop('properties')

    assert order == ref_response


async def test_invalid_rule_id_404(
        taxi_subvention_admin,
        mock_v1_retrieve_by_uniques,
        mock_v1_parks_orders_list,
        mock_bsx_v1_rules_match,
        mock_soc_v1_context,
        mock_oa_v1_order_proc_retrieve,
        mock_driver_mode_index_v1_mode_history,
        mockserver,
):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _handler(request):
        return mockserver.make_response(status=400)

    response = await taxi_subvention_admin.post(
        '/internal/subvention-admin/v1/nmfg/orders/match',
        json={
            'unique_driver_id': 'mock_udid',
            'time_range': {
                'start': '2022-03-01T00:00:00Z',
                'end': '2022-03-15T00:00:00Z',
            },
            'rule_id': 'incorrect_rule_id',
        },
    )

    assert response.status_code == 404


async def test_no_currency(
        taxi_subvention_admin,
        mock_v1_retrieve_by_uniques,
        mock_v1_parks_orders_list,
        mock_bs_v1_rules_select,
        mock_bsx_v1_rules_match,
        mock_soc_v1_context,
        mock_oa_v1_order_proc_retrieve,
        mock_driver_mode_index_v1_mode_history,
        mockserver,
):
    mock_oa_v1_order_proc_retrieve.set_doc({'_id': 'real_id'})

    response = await taxi_subvention_admin.post(
        '/internal/subvention-admin/v1/nmfg/orders/match',
        json={
            'unique_driver_id': 'mock_udid',
            'time_range': {
                'start': '2022-03-01T00:00:00Z',
                'end': '2022-03-15T00:00:00Z',
            },
            'rule_id': '4358d289-ac0b-4c66-acfb-802620392bb2',
        },
    )

    assert response.status_code == 200
    assert 'currency' not in response.json()['orders'][0]


async def test_dms_empty_response(
        taxi_subvention_admin,
        mock_v1_retrieve_by_uniques,
        mock_v1_parks_orders_list,
        mock_bs_v1_rules_select,
        mock_bsx_v1_rules_match,
        mock_soc_v1_context,
        mock_oa_v1_order_proc_retrieve,
        mockserver,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    async def handler(request):
        handler.req = request
        return {'docs': [], 'cursor': ''}

    response = await taxi_subvention_admin.post(
        '/internal/subvention-admin/v1/nmfg/orders/match',
        json={
            'unique_driver_id': 'mock_udid',
            'time_range': {
                'start': '2022-03-01T00:00:00Z',
                'end': '2022-03-15T00:00:00Z',
            },
            'rule_id': '4358d289-ac0b-4c66-acfb-802620392bb2',
        },
    )

    assert response.status_code == 200
    assert 'driver_mode' not in response.json()['orders'][0]
