import copy

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models


def set_modeler_eta_threshold(pgsql, threshold, depot_id=const.DEPOT_ID):
    cursor = pgsql['grocery_dispatch'].cursor()
    cursor.execute(
        'INSERT INTO dispatch.dispatch_eta_modeler_threshold '
        f'(depot_id, eta) VALUES (\'{depot_id}\', {threshold});',
    )


@pytest.mark.now(const.NOW)
@pytest.mark.experiments3(
    name='grocery_dispatch_modeler_decision',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'primary_modeler_name': 'promise'},
        },
    ],
    is_config=True,
)
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@pytest.mark.parametrize(
    ['exp_threshold', 'db_threshold', 'overwrite_db_value', 'should_fallback'],
    [
        (600, None, False, False),  # no fallback by exp value
        (300, None, False, True),  # fallback by exp value
        (600, 300, False, True),  # fallback by db value
        (600, 300, True, False),  # no fallback by exp value override
    ],
)
async def test_create_order_check_eta_threshold(
        taxi_grocery_dispatch,
        pgsql,
        cargo,
        experiments3,
        grocery_shifts,
        grocery_depots,
        testpoint,
        exp_threshold,
        db_threshold,
        overwrite_db_value,
        should_fallback,
):
    experiments3.add_config(
        name='grocery_dispatch_eta_modeler_threshold',
        consumers=['grocery_dispatch/depots'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'eta': exp_threshold,
            'overwrite_db_value': overwrite_db_value,
        },
    )
    if db_threshold:
        set_modeler_eta_threshold(pgsql, db_threshold)
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(const.DEPOT_ID), auto_add_zone=False,
    )
    grocery_shifts.set_couriers_shifts_response(
        {'depot_ids': [const.DEPOT_ID]},
    )

    await taxi_grocery_dispatch.invalidate_caches()

    if should_fallback:
        cargo.check_request(
            route_points=[models.FIRST_POINT, models.CLIENT_POINT],
            taxi_class='express',
            claim_kind='delivery_service',
            taxi_classes=['courier'],
        )
    else:
        first_point = copy.deepcopy(models.FIRST_POINT)
        first_point.comment = None

        cargo.check_request(
            route_points=[
                first_point,
                models.CLIENT_POINT,
                models.RETURN_POINT,
            ],
            taxi_class='lavka',
            claim_kind='platform_usage',
            taxi_classes=['lavka'],
        )

    @testpoint('yt_logger::messages::dispatch_modeler_decision_log')
    def on_modeler_decision_written_yt(data):
        expected_message = {
            'depot_id': const.DEPOT_ID,
            'order_id': const.SHORT_ORDER_ID,
            'modeler_name': 'promise',
            'is_used': True,
            'fallback': should_fallback,
        }
        for key in expected_message:
            assert data[key] == expected_message[key]

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', models.CREATE_REQUEST_DATA,
    )

    assert response.status_code == 200
    assert on_modeler_decision_written_yt.times_called == 1
