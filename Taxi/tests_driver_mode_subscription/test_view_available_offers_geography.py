import datetime
from typing import Optional
from typing import Set

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_NOW = '2019-05-01T05:00:00+00:00'
_LONG_AGO = datetime.datetime(2000, 5, 1, 5, 0, 0)

_OFFER_CARD_TITLE = 'offer_card_title'
_OFFER_CARD_SUBTITLE = 'offer_card_subtitle'
_OFFER_CARD_DESCRIPTION = 'offer_card_description'
_OFFER_HEADER = 'offer_header'
_OFFER_TEXT = 'offer_text'
_MEMO_HEADER = 'memo_header'
_MEMO_TEXT = 'memo_text'


@pytest.mark.now(_NOW)
@pytest.mark.experiments3(filename='work_mode_experiments.json')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(
    [
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
            'node_type': 'root',
            'parent_name': 'br_root',
            'tariff_zones': ['spb'],
            'region_id': '225',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_samara',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['samara'],
            'region_id': '51',
        },
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'orders',
            'geobooking': 'geobooking',
            'non_hierarchial_mode': 'orders',
            'enable_root': 'orders',
            'disable_root': 'orders',
            'disable_root_enable_moscow': 'orders',
            'enable_root_disable_moscow': 'orders',
            'enable_moscow_tariff_zone': 'orders',
            'enable_moscow_exp_match': 'orders',
            'enable_moscow_exp_mismatch': 'orders',
            'disable_moscow_tariff_zone': 'orders',
            'disable_parent_mismatching_experiment': 'orders',
            'disable_mode_enable_matching_experiment': 'orders',
            'default_mode': 'orders',
        },
    },
    DRIVER_MODE_GROUPS={
        'taxi': {'orders_provider': 'taxi', 'reset_modes': ['default_mode']},
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('non_hierarchial_mode'),
            mode_rules.Patch('enable_root'),
            mode_rules.Patch('disable_root'),
            mode_rules.Patch('disable_root_enable_moscow'),
            mode_rules.Patch('enable_root_disable_moscow'),
            mode_rules.Patch('enable_moscow_tariff_zone'),
            mode_rules.Patch('enable_moscow_exp_match'),
            mode_rules.Patch('enable_moscow_exp_mismatch'),
            mode_rules.Patch('disable_moscow_tariff_zone'),
            mode_rules.Patch('disable_parent_mismatching_experiment'),
            mode_rules.Patch('disable_mode_enable_matching_experiment'),
            mode_rules.Patch('default_mode'),
            mode_rules.Patch('custom_orders', stops_at=_LONG_AGO),
            mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, expected_available_modes, trackstory_position',
    [
        pytest.param(
            'orders',
            {
                'orders',
                'enable_root',
                'disable_root_enable_moscow',
                'enable_moscow_tariff_zone',
                'default_mode',
                'disable_mode_enable_matching_experiment',
            },
            scenario.MOSCOW_POSITION,
            id='moscow',
        ),
        pytest.param(
            'orders',
            {
                'orders',
                'enable_root',
                'enable_root_disable_moscow',
                'default_mode',
                'disable_mode_enable_matching_experiment',
            },
            scenario.SAMARA_POSITION,
            id='samara',
        ),
        pytest.param(
            'orders',
            {
                'orders',
                'enable_root',
                'enable_root_disable_moscow',
                'default_mode',
                'enable_moscow_exp_match',
                'disable_parent_mismatching_experiment',
            },
            scenario.SPB_POSITION,
            id='spb experiments',
        ),
        pytest.param(
            'orders',
            {'orders', 'default_mode'},  # TODO: allow enable_root mode
            None,
            id='no_position',
        ),
        pytest.param(
            'enable_root_disable_moscow',
            {'enable_root_disable_moscow', 'default_mode'},
            None,
            id='test_current_offer_available',
        ),
        pytest.param(
            'orders',
            {
                'default_mode',
                'disable_mode_enable_matching_experiment',
                'enable_root',
                'enable_root_disable_moscow',
                'orders',
            },
            scenario.SAMARA_POSITION,
            id='non hierarchial modes disabled, except default',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_available_by_default': [],
                    },
                ),
            ],
        ),
        pytest.param(
            'orders',
            {
                'default_mode',
                'disable_mode_enable_matching_experiment',
                'enable_root_disable_moscow',
                'enable_root',
                'orders',
                'non_hierarchial_mode',
            },
            scenario.SAMARA_POSITION,
            id='include work_modes_available_by_default',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_always_available': [],
                        'work_modes_available_by_default': [
                            'non_hierarchial_mode',
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            'orders',
            {
                'default_mode',
                'enable_moscow_tariff_zone',
                'orders',
                'non_hierarchial_mode',
            },
            None,
            id='include work_modes_ignoring_geo',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_always_available': [
                            'enable_moscow_tariff_zone',
                            'non_hierarchial_mode',
                        ],
                        'work_modes_available_by_default': [],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_view_available_offers_geography(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mockserver,
        mocked_time,
        pgsql,
        current_mode: str,
        expected_available_modes: Set[str],
        trackstory_position: Optional[common.Position],
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene({profile: driver.Mode(current_mode)})
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    scene.mock_driver_trackstory(mockserver, trackstory_position)

    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'enable_root', 'br_root', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_root', 'br_root', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_root_enable_moscow', 'br_root', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_root_enable_moscow', 'br_moscow', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_root_disable_moscow', 'br_root', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_root_disable_moscow', 'br_moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_moscow_tariff_zone', 'moscow', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_moscow_tariff_zone', 'moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'default_mode', 'br_root', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_moscow_exp_match',
                'spb',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', True,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'enable_moscow_exp_mismatch',
                'spb',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', True,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_parent_mismatching_experiment',
                'br_root',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', True,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_parent_mismatching_experiment',
                'spb',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', False,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_mode_enable_matching_experiment',
                'br_root',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', False,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'disable_mode_enable_matching_experiment',
                'spb',
                False,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment', True,
                    ),
                ],
            ),
        ],
        pgsql,
    )

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    available_modes = {item['id'] for item in response.json()['ui']['items']}

    assert available_modes == expected_available_modes
