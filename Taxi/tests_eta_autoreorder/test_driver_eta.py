# pylint: disable=import-error

import pytest

import tests_eta_autoreorder.utils as utils

ALL_ORDER_IDS = (
    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    '55b6c882da3f3dbc9ec2d8f3cd8d45a8',
)


def _tree_leaf_paths(tree, cur=()):
    if not tree or not isinstance(tree, dict):
        yield '.'.join(cur)
    else:
        for key, value in tree.items():
            for path in _tree_leaf_paths(value, cur + (key,)):
                yield path


@pytest.mark.now('2020-01-01T12:00:00+0000')
@pytest.mark.pgsql('eta_autoreorder', files=['orders.sql'])
@pytest.mark.config(
    ETA_AUTOREORDER_SERVICE_ENABLED=True, ETA_AUTOREORDER_ETA_CACHE_TTL=60,
)
@pytest.mark.parametrize(
    'minimum_candidates, time_interval_for_jump, expected_rule_applied',
    [
        # minimum candidates filter pass and time_interval_for_jump pass
        (3, 1, True),
        # time_interval_for_jump fail
        (3, 3, False),
        # minimum candidates fail
        (4, 1, False),
    ],
)
async def test_check_driver_eta(
        pgsql,
        taxi_eta_autoreorder,
        testpoint,
        redis_store,
        now,
        mockserver,
        load_json,
        minimum_candidates,
        time_interval_for_jump,
        expected_rule_applied,
        experiments3,
):
    @mockserver.json_handler(utils.DRIVER_ETA_HANDLER)
    def _mock_driver_eta(request):
        response = load_json('eta_response.json')
        response['classes']['vip']['estimated_time'] = 300
        return response

    @testpoint('geobus-eta_payload_processed')
    def redis_eta_payload_processed(cache):
        return cache

    @testpoint('has_valid_reorder_rule')
    def has_valid_reorder_rule(data):
        return data

    @testpoint('reorder_rule_applied_checks')
    def reorder_rule_applied_checks(applied_checks):
        return applied_checks

    experiments_json = load_json('experiments3_reorder_detection_rules.json')
    clauses_value = experiments_json['configs'][0]['clauses'][0]['value']
    clauses_value['minimum_candidates_for_autoreorder'] = minimum_candidates
    clauses_value['time_interval_for_jump'] = time_interval_for_jump
    experiments3.add_experiments_json(experiments_json)
    await taxi_eta_autoreorder.enable_testpoints()
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        1,
        time_left=300,
        distance_left=5000,
        cache_is_empty=False,
        order_ids=ALL_ORDER_IDS,
    )
    await utils.publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        5,
        cache_is_empty=False,
        order_ids=ALL_ORDER_IDS,
    )
    await taxi_eta_autoreorder.invalidate_caches()
    response = await taxi_eta_autoreorder.get('internal/check_reorder_rules')
    assert response.status_code == 200
    assert has_valid_reorder_rule.times_called == 1
    applied_checks = reorder_rule_applied_checks.next_call()['applied_checks']
    assert applied_checks == ['dist_rel_check']
    orders_fitting_rule = response.json()
    if expected_rule_applied:
        assert len(orders_fitting_rule) == 1
        fit_order_id = orders_fitting_rule[0]['id']
        assert fit_order_id == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    else:
        assert not orders_fitting_rule
