import copy

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.experiments3(
    name='grocery_dispatch_lavka_cargo_auth_token_key',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'always on',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'create_handler_type',
                                'arg_type': 'string',
                                'value': 'create_taxi',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {'token_key': 'b2b-taxi-auth-grocery-gbr'},
        },
    ],
    default_value={'token_key': 'b2b-taxi-auth-grocery-fra'},
    is_config=True,
)
@pytest.mark.parametrize('zone_type', ['yandex_taxi', 'pedestrian'])
async def test_create_with_auth(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        zone_type,
):

    exp3_recorder = experiments3.record_match_tries(
        'grocery_dispatch_lavka_cargo_auth_token_key',
    )
    if zone_type == 'pedestrian':
        cargo.check_authorization(authorization='Bearer CCC123')
    else:
        cargo.check_authorization(authorization='Bearer DDD123')
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)
    request_data['zone_type'] = zone_type
    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['region_id'] == 213
    assert match_tries[0].kwargs['country_iso3'] == 'RUS'

    if zone_type == 'pedestrian':
        assert (
            match_tries[0].kwargs['create_handler_type'] == 'create_accepted'
        )
    else:
        assert match_tries[0].kwargs['create_handler_type'] == 'create_taxi'

    assert response1.status_code == 200
