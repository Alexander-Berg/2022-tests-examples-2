from typing import Optional
from typing import Set

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

_NOW = '2019-05-01T05:00:00+00:00'

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
        'node_type': 'root',
        'parent_name': 'br_root',
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
]


def _init_geo_rules(pgsql):
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
        ],
        pgsql,
    )


@pytest.mark.now(_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.config(
    DRIVER_MODE_GROUPS={},
    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
        'work_modes_always_available': ['orders'],
        'work_modes_available_by_default': [],
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
            mode_rules.Patch('disable_moscow_tariff_zone'),
        ],
    ),
)
@pytest.mark.parametrize(
    'by_session',
    [pytest.param(False, id='tvm'), pytest.param(True, id='pro')],
)
@pytest.mark.parametrize(
    'current_work_mode, next_work_mode, expected_code, driver_position',
    [
        pytest.param(
            'orders',
            'non_hierarchial_mode',
            400,
            scenario.MOSCOW_POSITION,
            id='non_hierarchial_mode',
        ),
        pytest.param(
            'orders',
            'non_hierarchial_mode',
            200,
            scenario.MOSCOW_POSITION,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
                        'work_modes_available_by_default': [
                            'non_hierarchial_mode',
                        ],
                        'work_modes_always_available': [],
                    },
                ),
            ],
            id='non_hierarchial_mode_geography_defaults',
        ),
        pytest.param(
            'orders',
            'non_hierarchial_mode',
            423,
            None,
            id='non_hierarchial_mode_no_position',
        ),
        pytest.param(
            'orders',
            'enable_root',
            200,
            scenario.MOSCOW_POSITION,
            id='enabled_in_root',
        ),
        pytest.param(
            'orders',
            'disable_root',
            400,
            scenario.MOSCOW_POSITION,
            id='disabled_in_root',
        ),
        pytest.param(
            'orders',
            'disable_root_enable_moscow',
            200,
            scenario.MOSCOW_POSITION,
            id='enabled_in_moscow',
        ),
        pytest.param(
            'orders',
            'disable_root_enable_moscow',
            400,
            scenario.SAMARA_POSITION,
            id='enabled_in_moscow_driver_in_samara',
        ),
        pytest.param(
            'orders',
            'enable_root_disable_moscow',
            400,
            scenario.MOSCOW_POSITION,
            id='disabled_in_moscow',
        ),
        pytest.param(
            'orders',
            'enable_root_disable_moscow',
            200,
            scenario.SAMARA_POSITION,
            id='disabled_in_moscow_driver_in_samara',
        ),
        pytest.param(
            'orders',
            'disable_moscow_tariff_zone',
            400,
            scenario.SAMARA_POSITION,
            id='only_disabled_rule_for_different_zone',
        ),
        pytest.param(
            'orders',
            'disable_moscow_tariff_zone',
            400,
            scenario.MOSCOW_POSITION,
            id='only_disabled_rule_for_current_zone',
        ),
        pytest.param(
            'orders',
            'enable_moscow_tariff_zone',
            400,
            scenario.SAMARA_POSITION,
            id='only_enabled_rule_in_moscow_driver_is_samara',
        ),
        pytest.param(
            'orders',
            'enable_moscow_tariff_zone',
            423,
            None,
            id='hierarchial_mode_no_prosition',
        ),
        pytest.param(
            'orders',
            'enable_moscow_tariff_zone',
            200,
            scenario.MOSCOW_POSITION,
            id='driver_in_only_enabled_zone',
        ),
        pytest.param(
            'enable_moscow_tariff_zone',
            'orders',
            200,
            None,
            id='unsubscribe_from_geohierarchial_mode',
        ),
    ],
)
async def test_mode_set_geography_rules(
        taxi_driver_mode_subscription,
        mocked_time,
        mockserver,
        pgsql,
        mode_rules_data,
        current_work_mode: str,
        next_work_mode: str,
        expected_code: int,
        by_session: bool,
        driver_position: Optional[common.Position],
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene({profile: driver.Mode(current_work_mode)})
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    scene.mock_driver_trackstory(mockserver, driver_position)

    _init_geo_rules(pgsql)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile,
        next_work_mode,
        None,
        by_session,
    )
    assert response.status_code == expected_code


@pytest.mark.now(_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.config(DRIVER_MODE_GROUPS={})
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('disabled_mode_with_experiment'),
            mode_rules.Patch('mode_with_disabled_experiment'),
            mode_rules.Patch('mode_with_matched_experiment'),
            mode_rules.Patch('mode_with_mismatched_experiment'),
        ],
    ),
)
@pytest.mark.parametrize(
    'by_session',
    [pytest.param(False, id='tvm'), pytest.param(True, id='pro')],
)
@pytest.mark.experiments3(filename='work_mode_experiments.json')
@pytest.mark.parametrize(
    'current_work_mode, next_work_mode, expected_code, '
    'driver_position, expect_experiment_call, expected_kwargs_geonodes',
    [
        pytest.param(
            'orders',
            'mode_with_disabled_experiment',
            200,
            scenario.MOSCOW_POSITION,
            False,
            {},
            id='mode with disabled experiment available',
        ),
        pytest.param(
            'orders',
            'disabled_mode_with_experiment',
            400,
            scenario.MOSCOW_POSITION,
            False,
            {},
            id='disabled mode not use experiments',
        ),
        pytest.param(
            'orders',
            'mode_with_matched_experiment',
            200,
            scenario.MOSCOW_POSITION,
            True,
            {'br_root', 'br_russia', 'br_moscow', 'moscow'},
            id='mode with matched experiment',
        ),
        pytest.param(
            'orders',
            'mode_with_mismatched_experiment',
            400,
            scenario.MOSCOW_POSITION,
            True,
            {'br_root', 'br_russia', 'br_moscow', 'moscow'},
            id='mode with mismatched experiment',
        ),
    ],
)
async def test_mode_set_geography_rules_experiments(
        taxi_driver_mode_subscription,
        mocked_time,
        mockserver,
        mode_rules_data,
        experiments3,
        pgsql,
        current_work_mode: str,
        next_work_mode: str,
        expected_code: int,
        by_session: bool,
        driver_position: Optional[common.Position],
        expect_experiment_call: bool,
        expected_kwargs_geonodes: Set[str],
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene({profile: driver.Mode(current_work_mode)})
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    scene.mock_driver_trackstory(mockserver, driver_position)

    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'disabled_mode_with_experiment',
                'br_russia',
                False,
                [
                    geography_tools.ModeGeographyExperiment(
                        'always_enabled_exp', True,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_with_disabled_experiment',
                'br_moscow',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'always_disabled_exp', False,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_with_matched_experiment',
                'br_russia',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment_1', True,
                    ),
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment_2', True,
                    ),
                ],
            ),
            geography_tools.ModeGeographyConfiguration(
                'mode_with_mismatched_experiment',
                'br_moscow',
                True,
                [
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment_1', True,
                    ),
                    geography_tools.ModeGeographyExperiment(
                        'mode_experiment_2', True,
                    ),
                ],
            ),
        ],
        pgsql,
    )

    exp3_recorder = experiments3.record_match_tries('mode_experiment_1')

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile,
        next_work_mode,
        None,
        by_session,
    )
    assert response.status_code == expected_code

    if expect_experiment_call:
        match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
        exp_kwargs = match_tries[0].kwargs
        assert exp_kwargs['work_mode'] == next_work_mode
        assert exp_kwargs['park_id'] == profile.park_id()
        assert exp_kwargs['driver_profile_id'] == profile.profile_id()
        assert set(exp_kwargs['geonodes']) == expected_kwargs_geonodes


@pytest.mark.now(_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
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
@pytest.mark.config(DRIVER_MODE_GROUPS={})
@pytest.mark.parametrize(
    'next_mode, by_session, expected_code',
    [
        pytest.param(driver.Mode('orders'), False, 423, id='different_mode'),
        pytest.param(
            driver.Mode(
                'driver_fix',
                mode_settings={
                    'rule_id': 'id2',
                    'shift_close_time': '00:00:00',
                },
            ),
            False,
            200,
            id='same_mode',
        ),
        pytest.param(
            driver.Mode(
                'driver_fix',
                mode_settings={
                    'rule_id': 'id2',
                    'shift_close_time': '00:00:00',
                },
            ),
            True,
            423,
            id='same_mode_from_pro',
        ),
    ],
)
async def test_mode_set_geography_rules_resubscribe(
        taxi_driver_mode_subscription,
        mocked_time,
        mockserver,
        pgsql,
        mode_rules_data,
        next_mode: driver.Mode,
        expected_code: int,
        by_session: bool,
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene(
        {
            profile: driver.Mode(
                'driver_fix',
                mode_settings={
                    'rule_id': 'id1',
                    'shift_close_time': '00:00:00',
                },
            ),
        },
    )
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    scene.mock_driver_trackstory(mockserver, driver_position=None)

    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'orders', 'br_moscow', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'driver_fix', 'br_moscow', False,
            ),
        ],
        pgsql,
    )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile,
        next_mode.work_mode,
        next_mode.mode_settings,
        by_session,
    )
    assert response.status_code == expected_code


@pytest.mark.now(_NOW)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.config(DRIVER_MODE_GROUPS={})
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('non_hierarchial_mode'),
            mode_rules.Patch('enable_root'),
            mode_rules.Patch('disable_root'),
            mode_rules.Patch('disable_root_enable_moscow'),
            mode_rules.Patch('enable_root_disable_moscow'),
            mode_rules.Patch('enable_moscow_tariff_zone'),
            mode_rules.Patch('disable_moscow_tariff_zone'),
        ],
    ),
)
async def test_mode_set_geography_rules_fallback_position(
        taxi_driver_mode_subscription,
        mocked_time,
        mockserver,
        pgsql,
        mode_rules_data,
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene({profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    scene.mock_driver_trackstory(mockserver, driver_position=None)

    _init_geo_rules(pgsql)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile,
        work_mode='enable_moscow_tariff_zone',
        mode_settings=None,
        set_by_session=False,
        fallback_position=scenario.MOSCOW_POSITION,
    )
    assert response.status_code == 200
