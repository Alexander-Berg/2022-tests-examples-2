import itertools

import bson
import pytest


def _make_experiment(order_id):
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'rule_type',
                                    'arg_type': 'string',
                                    'value': 'subvention_check_order',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': order_id,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'enabled': True},
            },
        ],
    }


def _make_request(order_id, time, distance, types):
    return {
        'order': {
            'id': order_id,
            'transporting_time': time,
            'transporting_distance': distance,
        },
        'subventions': [{'type': t} for t in types],
    }


async def _request(uafs, order_id, time, distance, types):
    return await uafs.post(
        'v2/subvention/check_order',
        _make_request(order_id, time, distance, types),
    )


async def _test_base(uafs):
    subvention_types = ['single_ride', 'single_ontop', 'goal']

    for types in [
            p
            for r in range(1, len(subvention_types) + 1)
            for p in itertools.permutations(subvention_types, r=r)
    ]:
        response = await _request(uafs, 'order_id1', 10, 20, types)

        assert response.status_code == 200
        assert response.json() == {'statuses': {t: 'allow' for t in types}}


async def test_base1(taxi_uantifraud):
    await _test_base(taxi_uantifraud)


@pytest.mark.experiments3(**_make_experiment('order_id1'))
async def test_base2(taxi_uantifraud, testpoint):
    @testpoint('view_wrapper_not_rules')
    def _not_rules_tp(_):
        pass

    await _test_base(taxi_uantifraud)
    assert await _not_rules_tp.wait_call()


@pytest.mark.experiments3(**_make_experiment('order_id1'))
@pytest.mark.config(UAFS_SUBVENTION_CHECK_ORDER_CORE_REQUEST_ENABLED=True)
async def test_args(taxi_uantifraud, testpoint, mockserver):
    subvention_types = ['single_ride', 'single_ontop', 'goal']
    req = _make_request('order_id1', 30, 40, subvention_types)
    resp = {'single_ride': 'allow', 'goal': 'block'}
    order_core_resp = {
        'document': {
            'processing': {'version': 33},
            '_id': 'order_id1',
            'order': {
                'version': 32,
                'performer': {'tariff': {'class': 'econom'}},
                'taximeter_receipt': {
                    'total_distance': 17278,
                    'total_duration': 1146,
                },
                'request': {'source': {'country': 'Россия'}},
                'route': {'distance': 11566.527506113065, 'time': 1538},
                'pricing_data': {'user': {'data': {'country_code2': 'RU'}}},
                'calc_method': 'fixed',
                'fixed_price_discard_reason': 'far_from_b',
            },
        },
        'revision': {'order.version': 32, 'processing.version': 33},
    }

    rules_triggered = []
    rules_passed = []

    @testpoint('rule_exec_triggered')
    def rule_exec_triggered_tp(rule):  # pylint: disable=W0612
        rules_triggered.append(rule['rule_id'])

    @testpoint('rule_exec_passed')
    def rule_exec_passed_tp(rule):  # pylint: disable=W0612
        rules_passed.append(rule['rule_id'])

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {
            **req,
            **{'auto_entity_map': {}},
            **{'order_core': order_core_resp['document']},
        }
        return resp

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _order_core_get_fields(request):
        assert request.args['order_id'] == 'order_id1'
        assert bson.BSON.decode(request.get_data()) == {
            'fields': [
                'order.calc_method',
                'order.fixed_price_discard_reason',
                'order.performer.tariff.class',
                'order.pricing_data.user.data.country_code2',
                'order.request.source.country',
                'order.route.distance',
                'order.route.time',
                'order.taximeter_receipt.total_distance',
                'order.taximeter_receipt.total_duration',
            ],
        }
        return mockserver.make_response(
            bson.BSON.encode(order_core_resp), status=200,
        )

    response = await taxi_uantifraud.post(
        'v2/subvention/check_order', json=req,
    )

    assert response.status_code == 200
    assert response.json() == {
        'statuses': {**resp, **{'single_ontop': 'allow'}},
    }

    assert await _order_core_get_fields.wait_call()
    assert await test_args_tp.wait_call()

    assert rules_triggered == ['test_rule2', 'test_rule1']
    assert rules_passed == ['test_rule3']
