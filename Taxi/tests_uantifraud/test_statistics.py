import asyncio

import pytest

_CARD_VERIFY_REQUIRED_REQUEST = {
    'service': 'service',
    'service_type': 'service_type',
    'app_metrica_device_id': 'E030F317-4FE0-4EE0-8C0B-42EA9BC4F552',
    'app_metrica_uuid': 'app_metrica_uuid',
    'cards': [
        {
            'id': 'card_id1',
            'number': 'card_number1',
            'verification_details': {
                'level': 'card_level1',
                'service_id': 1,
                'verified_at': '2021-01-10T09:10:11+03:00',
            },
        },
    ],
}


def _make_experiment():
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'value': {'enabled': True},
                'predicate': {'init': {}, 'type': 'true'},
            },
        ],
    }


async def _make_request(uafs, i):
    resp = await uafs.post(
        '/v1/card/verification/required',
        json={**_CARD_VERIFY_REQUIRED_REQUEST, **{'service': f'service_{i}'}},
        headers={
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': f'4023520426_{i}',
        },
    )
    assert resp.status_code == 200


@pytest.mark.experiments3(**_make_experiment())
async def test_base(taxi_uantifraud, taxi_uantifraud_monitor):
    await taxi_uantifraud.tests_control(reset_metrics=True)

    await asyncio.gather(
        *[_make_request(taxi_uantifraud, i) for i in range(16)],
    )

    stats_resp = await taxi_uantifraud_monitor.get_metrics()
    assert stats_resp['js_executor_stats']['rules'] == {
        'failed': {
            '$meta': {'solomon_children_labels': 'id'},
            'test_failed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 16,
            },
            'test_failed_rule2': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 16,
            },
            'test_passed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_passed_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_triggered_prod_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_triggered_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
        },
        'passed': {
            '$meta': {'solomon_children_labels': 'id'},
            'test_failed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_failed_rule2': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_passed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 16,
            },
            'test_passed_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 16,
            },
            'test_triggered_prod_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
            'test_triggered_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': 0,
            },
        },
        'triggered': {
            '$meta': {'solomon_children_labels': 'id'},
            'test_failed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 0,
                    'test': 0,
                },
            },
            'test_failed_rule2': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 0,
                    'test': 0,
                },
            },
            'test_passed_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 0,
                    'test': 0,
                },
            },
            'test_passed_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 0,
                    'test': 0,
                },
            },
            'test_triggered_prod_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 16,
                    'test': 0,
                },
            },
            'test_triggered_test_rule1': {
                '$meta': {'solomon_children_labels': 'type'},
                'card_verify_required': {
                    '$meta': {'solomon_children_labels': 'mode'},
                    'prod': 0,
                    'test': 16,
                },
            },
        },
    }
    for metric in ['min', 'max', 'avg']:
        assert metric in stats_resp['js_executor_stats']['queue_size']['1min']
        assert (
            metric in stats_resp['js_executor_stats']['wrappers_count']['1min']
        )
        assert (
            metric
            in stats_resp['js_executor_stats']['wrappers_objects_count'][
                '1min'
            ]
        )
        assert (
            metric
            in stats_resp['js_executor_stats']['wrappers_primitives_count'][
                '1min'
            ]
        )


@pytest.mark.experiments3(**_make_experiment())
async def test_js_queue_overflow(taxi_uantifraud, testpoint):
    @testpoint('js_executer_queue_overflow')
    def _js_executer_queue_overflow_tp(_):
        pass

    await asyncio.gather(
        *[_make_request(taxi_uantifraud, i) for i in range(32)],
    )

    await _js_executer_queue_overflow_tp.wait_call()
