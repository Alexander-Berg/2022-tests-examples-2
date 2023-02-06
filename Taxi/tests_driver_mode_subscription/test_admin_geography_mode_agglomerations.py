from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules

_REQUEST_HEADERS = {
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
    'Accept-Language': 'ru',
}
_BY_EXPERIMENTS_HINT = 'enabled by experiments'


class ModeGeoNode:
    def __init__(
            self,
            name: str,
            is_enabled: bool = True,
            by_configs: Optional[str] = None,
            by_experiments: Optional[str] = None,
    ):
        self.name = name
        self.is_enabled = is_enabled
        self.hint = None
        if by_configs:
            self.hint = {'icon': 'by_configs', 'title': by_configs}
        elif by_experiments:
            self.hint = {'icon': 'by_experiments', 'title': by_experiments}

    def to_json(self):
        json = {'name': self.name, 'is_enabled': self.is_enabled}
        if self.hint:
            json['hint'] = self.hint
        return json


def from_geo_nodes(agglomerations: List[ModeGeoNode]):
    return [node.to_json() for node in agglomerations]


async def _request_nodes_list(
        taxi_driver_mode_subscription, work_mode: str,
) -> Dict[str, Any]:
    handler_url = 'v1/admin/geography/work-mode-agglomerations-list'
    response = await taxi_driver_mode_subscription.get(
        f'{handler_url}?work_mode={work_mode}', headers=_REQUEST_HEADERS,
    )
    assert response.status_code == 200

    return response.json()


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_murino',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['moscow'],
        },
    ],
)
@pytest.mark.config(
    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
        'work_modes_available_by_default': [],
        'work_modes_always_available': [],
    },
)
@pytest.mark.parametrize(
    'work_mode, expected_geo_nodes, expected_warning_message',
    [
        pytest.param(
            'orders',
            [ModeGeoNode(name='br_root', by_configs='DRIVER_MODE_GROUPS')],
            'Внимание! Агломерации: br_root.',
            id='default_mode',
        ),
        pytest.param(
            'unknown-mode-name', [], None, id='no_geography_for_unknown_mode',
        ),
    ],
)
async def test_default_modes(
        taxi_driver_mode_subscription,
        work_mode: str,
        expected_geo_nodes: List[ModeGeoNode],
        expected_warning_message: Optional[str],
):
    response = await _request_nodes_list(
        taxi_driver_mode_subscription, work_mode=work_mode,
    )

    expected_agglomerations = from_geo_nodes(expected_geo_nodes)
    agglomerations = response['agglomerations']
    warning_message = response.get('warning_message', None)
    assert agglomerations == expected_agglomerations
    assert warning_message == expected_warning_message


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_WARNING_AGGLOMERATIONS={
        'included_depth': 2,
        'excluded': ['br_spb'],
    },
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_murino',
            'name_en': 'Murino',
            'name_ru': 'Мурино',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['murino'],
        },
        {
            'name': 'br_spb',
            'name_en': 'Spb',
            'name_ru': 'Спб',
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['spb'],
        },
    ],
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[mode_rules.Patch(rule_name='murino-fix')],
        ),
    ],
)
@pytest.mark.parametrize(
    'geo_rules, work_mode, expected_geo_nodes, expected_warning_message',
    [
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix', geo_node='br_spb', is_enabled=True,
                ),
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='br_pulkovo',
                    is_enabled=False,
                ),
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='br_murino',
                    is_enabled=True,
                    experiments=[
                        geography_tools.ModeGeographyExperiment('exp1', True),
                        geography_tools.ModeGeographyExperiment('exp2', False),
                    ],
                ),
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix', geo_node='murino', is_enabled=True,
                ),
            ],
            'murino-fix',
            [
                ModeGeoNode('br_murino', by_experiments=_BY_EXPERIMENTS_HINT),
                ModeGeoNode('br_pulkovo', is_enabled=False),
                ModeGeoNode('br_spb', is_enabled=True),
                ModeGeoNode('murino', is_enabled=True),
            ],
            'Внимание! Агломерации: br_murino.',
            id='geography_mixed_with_experiments',
        ),
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='br_murino',
                    is_enabled=True,
                ),
            ],
            'murino-fix',
            [ModeGeoNode('br_murino', is_enabled=True)],
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WARNING_AGGLOMERATIONS={
                        'included_depth': 2,
                        'excluded': ['br_murino'],
                    },
                ),
            ],
            id='single_agglomeration',
        ),
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='br_murino',
                    is_enabled=False,
                ),
            ],
            'murino-fix',
            [ModeGeoNode('br_murino', is_enabled=False)],
            None,
            id='single_disabled_agglomeration',
        ),
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='orders', geo_node='br_murino', is_enabled=False,
                ),
            ],
            'orders',
            [ModeGeoNode('br_root', by_configs='DRIVER_MODE_GROUPS')],
            'Внимание! Агломерации: br_root.',
            id='ignore_geography_by_configs',
        ),
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='br_murino',
                    is_enabled=True,
                    experiments=[
                        geography_tools.ModeGeographyExperiment(
                            'murino', False,
                        ),
                    ],
                ),
            ],
            'murino-fix',
            [ModeGeoNode('br_murino', is_enabled=True)],
            'Внимание! Агломерации: br_murino.',
            id='enable_mode_ignoring_disabled_experiments',
        ),
        pytest.param(
            [],
            'murino-fix',
            [
                ModeGeoNode(
                    'br_root', by_configs='DRIVER_MODE_GEOGRAPHY_DEFAULTS',
                ),
            ],
            'Внимание! Агломерации: br_root.',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_available_by_default': ['murino-fix'],
                    },
                ),
            ],
            id='enable_global_geography_by_geography_defaults_1',
        ),
        pytest.param(
            [],
            'murino-fix',
            [
                ModeGeoNode(
                    'br_root', by_configs='DRIVER_MODE_GEOGRAPHY_DEFAULTS',
                ),
            ],
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_available_by_default': [],
                        'work_modes_always_available': ['murino-fix'],
                    },
                    DRIVER_MODE_SUBSCRIPTION_WARNING_AGGLOMERATIONS={
                        'included_depth': 0,
                        'excluded': [],
                    },
                ),
            ],
            id='enable_global_geography_by_geography_defaults_2',
        ),
        pytest.param(
            [
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='unknown_node_1',
                    is_enabled=True,
                ),
                geography_tools.ModeGeographyConfiguration(
                    work_mode='murino-fix',
                    geo_node='unknown_node_2',
                    is_enabled=False,
                ),
            ],
            'murino-fix',
            [
                ModeGeoNode('unknown_node_1', is_enabled=True),
                ModeGeoNode('unknown_node_2', is_enabled=False),
            ],
            None,
            id='unknown geo node not crash endpoint',
        ),
    ],
)
async def test_geography(
        taxi_driver_mode_subscription,
        pgsql,
        geo_rules: List[geography_tools.ModeGeographyConfiguration],
        work_mode: str,
        expected_geo_nodes: List[ModeGeoNode],
        expected_warning_message: Optional[str],
):
    geography_tools.insert_mode_geography(geo_rules, pgsql)

    response = await _request_nodes_list(
        taxi_driver_mode_subscription, work_mode=work_mode,
    )

    expected_agglomerations = from_geo_nodes(expected_geo_nodes)
    agglomerations = response['agglomerations']
    warning_message = response.get('warning_message', None)
    assert agglomerations == expected_agglomerations
    assert warning_message == expected_warning_message
