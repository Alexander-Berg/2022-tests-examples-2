import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
_NOW = dt.datetime(2020, 5, 5, 15, 15, 5, 0, tzinfo=pytz.utc)
_FUTURE_DATE = _NOW + dt.timedelta(days=3)
_PAST_DATE = _NOW - dt.timedelta(days=3)

_REQUEST_HEADER = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

_DEFAULT_GEONODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'agglomeration',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'agglomeration',
        'parent_name': 'br_russia',
        'tariff_zones': ['moscow'],
    },
    {
        'name': 'br_spb',
        'name_en': 'St. Petersburg',
        'name_ru': 'Cанкт-Петербург',
        'node_type': 'agglomeration',
        'parent_name': 'br_russia',
        'tariff_zones': ['spb'],
        'region_id': '2',
    },
    {
        'name': 'br_uk',
        'name_en': 'UK',
        'name_ru': 'Великобритания',
        'node_type': 'agglomeration',
        'parent_name': 'br_root',
        'tariff_zones': ['london'],
        'region_id': '102',
    },
]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(rule_name='mode_without_stops_at'),
                mode_rules.Patch(
                    rule_name='mode_with_stops_at_in_future',
                    stops_at=_FUTURE_DATE,
                ),
                mode_rules.Patch(
                    rule_name='mode_already_stoped', stops_at=_PAST_DATE,
                ),
                mode_rules.Patch(
                    rule_name='mode_canceled',
                    stops_at=_FUTURE_DATE,
                    is_canceled=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_admin_geography_aglomerations_with_config(
        taxi_driver_mode_subscription, pgsql,
):
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'mode_without_stops_at', 'br_moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_with_stops_at_in_future', 'br_root', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_already_stoped', 'br_spb', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_canceled', 'br_samara', False,
            ),
        ],
        pgsql,
    )

    response = await taxi_driver_mode_subscription.get(
        'v1/admin/geography/configured-agglomerations-list',
        json={},
        headers=_REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'agglomerations': [
            {'has_all_mode_rules_outdated': False, 'name': 'br_moscow'},
            {'has_all_mode_rules_outdated': False, 'name': 'br_root'},
            {'has_all_mode_rules_outdated': True, 'name': 'br_samara'},
            {'has_all_mode_rules_outdated': True, 'name': 'br_spb'},
        ],
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(rule_name='disable_russia_enable_br_moscow'),
                mode_rules.Patch(rule_name='enable_russia_disable_br_moscow'),
                mode_rules.Patch(rule_name='disable_moscow'),
                mode_rules.Patch(rule_name='enable_moscow'),
                mode_rules.Patch(rule_name='enable_spb'),
                mode_rules.Patch(rule_name='disable_spb'),
                mode_rules.Patch(rule_name='experimental_mode'),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'agglomeration, origin, expected_code, expected_response',
    [
        pytest.param(
            'br_russia',
            None,
            200,
            {
                'work_modes': [
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'disable_russia_enable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'enable_russia_disable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'experimental_mode',
                            'experiments': [
                                {
                                    'name': 'exp1',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp2',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp3',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp4',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                            ],
                        },
                    },
                ],
            },
            id='russia',
        ),
        pytest.param(
            'moscow',
            None,
            200,
            {
                'work_modes': [
                    {
                        'origin_agglomeration_name': 'moscow',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'disable_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_moscow',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'disable_russia_enable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'moscow',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'enable_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_moscow',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'enable_russia_disable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'experimental_mode',
                            'experiments': [
                                {
                                    'name': 'exp1',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp2',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp3',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp4',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                            ],
                        },
                    },
                ],
            },
            id='moscow',
        ),
        pytest.param(
            'spb',
            'all',
            200,
            {
                'work_modes': [
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'disable_russia_enable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'spb',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'disable_spb',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'enable_russia_disable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'spb',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'enable_spb',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'spb',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'experimental_mode',
                            'experiments': [
                                {
                                    'name': 'exp1',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp2',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp3',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'spb',
                                },
                                {
                                    'name': 'exp4',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'spb',
                                },
                                {
                                    'name': 'exp5',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'spb',
                                },
                                {
                                    'name': 'exp6',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'spb',
                                },
                            ],
                        },
                    },
                ],
            },
            id='spb',
        ),
        pytest.param(
            'moscow',
            'parent_nodes',
            200,
            {
                'work_modes': [
                    {
                        'origin_agglomeration_name': 'br_moscow',
                        'work_mode_config': {
                            'is_enabled': True,
                            'work_mode': 'disable_russia_enable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_moscow',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'enable_russia_disable_br_moscow',
                            'experiments': [],
                        },
                    },
                    {
                        'origin_agglomeration_name': 'br_russia',
                        'work_mode_config': {
                            'is_enabled': False,
                            'work_mode': 'experimental_mode',
                            'experiments': [
                                {
                                    'name': 'exp1',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp2',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp3',
                                    'is_enabled': False,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                                {
                                    'name': 'exp4',
                                    'is_enabled': True,
                                    'origin_agglomeration_name': 'br_russia',
                                },
                            ],
                        },
                    },
                ],
            },
            id='inherited',
        ),
        pytest.param('london', None, 200, {'work_modes': []}, id='london'),
        pytest.param(
            'za_garazhami',
            None,
            400,
            {
                'code': 'INVALID_GEO_NODE',
                'message': 'geo_node za_garazhami not found',
                'details': 'geo_node za_garazhami not found',
            },
            id='invalid_node',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_admin_geography_fetch_configuration(
        taxi_driver_mode_subscription,
        pgsql,
        agglomeration: str,
        origin: Optional[str],
        expected_code: int,
        expected_response: Dict[str, Any],
):
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'disable_russia_enable_br_moscow', 'br_russia', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_russia_enable_br_moscow', 'br_moscow', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_russia_disable_br_moscow', 'br_russia', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_russia_disable_br_moscow', 'br_moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_moscow', 'moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_moscow', 'moscow', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_spb', 'spb', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_spb', 'spb', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'experimental_mode',
                'br_russia',
                False,
                [
                    geography_tools.ModeGeographyExperiment('exp1', False),
                    geography_tools.ModeGeographyExperiment('exp2', True),
                    geography_tools.ModeGeographyExperiment('exp3', False),
                    geography_tools.ModeGeographyExperiment('exp4', True),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'experimental_mode',
                'spb',
                True,
                [
                    geography_tools.ModeGeographyExperiment('exp3', True),
                    geography_tools.ModeGeographyExperiment('exp4', False),
                    geography_tools.ModeGeographyExperiment('exp5', False),
                    geography_tools.ModeGeographyExperiment('exp6', True),
                ],
            ),
        ],
        pgsql,
    )

    request_data: Dict[str, Any] = {'agglomeration': {'name': agglomeration}}
    if origin:
        request_data['origin'] = origin

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/geography/fetch-configuration',
        json=request_data,
        headers=_REQUEST_HEADER,
    )
    assert response.status_code == expected_code

    response_data = response.json()
    assert response_data == expected_response


_INITIAL_GEO_RULES = [
    geography_tools.ModeGeographyConfiguration(
        'changing_configuration',
        'br_root',
        True,
        [geography_tools.ModeGeographyExperiment('exp1', False)],
    ),
    geography_tools.ModeGeographyConfiguration(
        'changing_configuration',
        'moscow',
        True,
        [
            geography_tools.ModeGeographyExperiment('exp1', True),
            geography_tools.ModeGeographyExperiment('exp2', False),
        ],
    ),
    geography_tools.ModeGeographyConfiguration(
        'removing_configuration',
        'br_root',
        False,
        [geography_tools.ModeGeographyExperiment('exp1', True)],
    ),
    geography_tools.ModeGeographyConfiguration(
        'removing_configuration',
        'moscow',
        False,
        [
            geography_tools.ModeGeographyExperiment('exp1', False),
            geography_tools.ModeGeographyExperiment('exp2', True),
        ],
    ),
]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(rule_name='removing_configuration'),
                mode_rules.Patch(rule_name='changing_configuration'),
                mode_rules.Patch(rule_name='new_configuration'),
            ],
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.parametrize('is_check_request', [True, False])
async def test_admin_geography_rollout(
        taxi_driver_mode_subscription, pgsql, is_check_request: bool,
):
    geography_tools.insert_mode_geography(_INITIAL_GEO_RULES, pgsql)

    agglomeration = 'moscow'
    request_data: Dict[str, Any] = {
        'agglomeration': {'name': agglomeration},
        'work_mode_commands': [
            {
                'action': 'configure',
                'work_mode_config': {
                    'work_mode': 'new_configuration',
                    'is_enabled': True,
                    'experiments': [
                        {'name': 'exp1', 'is_enabled': True},
                        {'name': 'exp2', 'is_enabled': False},
                    ],
                },
            },
            {'action': 'reset', 'work_mode': 'removing_configuration'},
            {
                'action': 'configure',
                'work_mode_config': {
                    'work_mode': 'changing_configuration',
                    'is_enabled': False,
                    'experiments': [
                        {'name': 'exp3', 'is_enabled': True},
                        {'name': 'exp4', 'is_enabled': False},
                    ],
                },
            },
        ],
    }

    endpoint = 'check-rollout' if is_check_request else 'rollout'
    response = await taxi_driver_mode_subscription.post(
        f'v1/admin/geography/{endpoint}',
        json=request_data,
        headers=_REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    if is_check_request:
        assert response_data == {
            'data': request_data,
            'change_doc_id': request_data['agglomeration']['name'],
        }
        assert (
            geography_tools.fetch_geography_rules(pgsql) == _INITIAL_GEO_RULES
        )
    else:
        assert response_data == {}
        assert geography_tools.fetch_geography_rules(pgsql) == [
            geography_tools.ModeGeographyConfiguration(
                'changing_configuration',
                'br_root',
                True,
                [geography_tools.ModeGeographyExperiment('exp1', False)],
            ),
            geography_tools.ModeGeographyConfiguration(
                'changing_configuration',
                'moscow',
                False,
                [
                    geography_tools.ModeGeographyExperiment('exp3', True),
                    geography_tools.ModeGeographyExperiment('exp4', False),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'new_configuration',
                'moscow',
                True,
                [
                    geography_tools.ModeGeographyExperiment('exp1', True),
                    geography_tools.ModeGeographyExperiment('exp2', False),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'removing_configuration',
                'br_root',
                False,
                [geography_tools.ModeGeographyExperiment('exp1', True)],
            ),
        ]
