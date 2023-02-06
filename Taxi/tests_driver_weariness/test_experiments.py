import datetime
import json

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools


_NOW = datetime.datetime(2020, 1, 1)
_PLUS1 = _NOW + datetime.timedelta(hours=1)
_MSK = 37.1946401739712, 55.478983901730004
_TULA = 37.6, 54.2
_DEFAULT_EXPERIMENT_VALUES = (
    360,
    1080,
    900,
    ['driving', 'waiting', 'transporting'],
)


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_moskovskaja_obl',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['moscow', 'tula'],
            'region_id': '213',
        },
        {
            'name': 'br_moscow_middle_region',
            'name_en': 'Moscow (Middle Region)',
            'name_ru': 'Москва (среднее)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
        },
        {
            'name': 'br_moskovskaja_obl',
            'node_type': 'node',
            'name_en': 'Moscow Region',
            'name_ru': 'Московская область',
            'parent_name': 'br_tsentralnyj_fo',
            'region_id': '1',
        },
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
            'node_type': 'country',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'region_id': '3',
        },
    ],
)
@pytest.mark.match_tags(
    entity_type='udid', entity_value='unique7', entity_tags=['some_tag'],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.config(DRIVER_WEARINESS_ENABLE_TAGS_FETCHING=True)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.pgsql(
    'drivers_status_ranges',
    queries=[
        weariness_tools.insert_range(f'dbid_uuid{i}0', _NOW, _PLUS1)
        for i in range(4, 8)
    ]
    + [weariness_tools.insert_driver(i, f'unique{i}') for i in range(4, 8)]
    + [
        weariness_tools.insert_coordinate(4, _MSK[0], _MSK[1], _NOW),
        weariness_tools.insert_coordinate(5, 1.0, 1.0, _NOW),
        weariness_tools.insert_coordinate(7, _TULA[0], _TULA[1], _NOW),
    ],
)
@pytest.mark.parametrize(
    'unique_driver_id',
    [
        pytest.param('unique4', id='driver matched first exp clause'),
        pytest.param('unique5', id='default value matched'),
        pytest.param('unique6', id='default value matched'),
        pytest.param(
            'unique7', id='driver matched second exp clause with tags passed',
        ),
    ],
)
async def test_driver_weariness(
        taxi_driver_weariness, unique_driver_id: str, testpoint,
):
    @testpoint('enabled-experiment-match')
    def enabled_experiment_match(arg):
        experiment_values = {
            'unique4': (1000, 1, 1, ['transporting']),
            'unique7': (1200, 1, 1, ['driving', 'transporting']),
        }
        udid = arg['unique_driver_id']
        values = experiment_values.get(udid, _DEFAULT_EXPERIMENT_VALUES)
        assert arg['long_rest_m'] == values[0]
        assert arg['max_no_rest_m'] == values[1]
        assert arg['max_work_m'] == values[2]
        assert sorted(arg['working_order_statuses']) == sorted(values[3])

    response = await taxi_driver_weariness.post(
        'v1/driver-weariness',
        data=json.dumps({'unique_driver_id': unique_driver_id}),
    )
    assert response.status_code == 200
    assert enabled_experiment_match.times_called == 5
