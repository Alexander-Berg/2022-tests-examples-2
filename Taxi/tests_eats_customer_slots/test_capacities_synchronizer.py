import datetime

import pytest

from tests_eats_customer_slots import utils

DISTLOCK_TASK_NAME = 'intervals-capacities-synchronizer'


def make_expected_db_state(yaml_data):
    values = yaml_data.get('values')
    result = []
    for row in values:
        datetime_format = '%Y-%m-%d %H:%M:%S%z'
        interval = {}
        interval['interval_start'] = datetime.datetime.strptime(
            row['interval_start'], datetime_format,
        )
        interval['interval_end'] = datetime.datetime.strptime(
            row['interval_end'], datetime_format,
        )
        interval['capacity'] = row['capacity']
        place = {}
        place['place_id'] = row['place_id']
        place['logistics_group_id'] = row['logistics_group_id']
        place['capacities'] = []
        place['capacities'].append(interval)
        if result and result[-1]['place_id'] == row['place_id']:
            result[-1]['capacities'].append(interval)
        else:
            result.append(place)
    return result


@pytest.mark.config(
    EATS_CUSTOMER_SLOTS_CAPACITIES_SYNCHRONIZER={
        'yql_retry_interval_ms': 100,
        'yql_total_wait_ms': 300,
        'yql_read_limit': 20,
        'insert_batch_size': 2,
        'period_seconds': 3600,
    },
)
@pytest.mark.yt(
    schemas=['yt_current_capacity.yaml'],
    static_table_data=['yt_current_capacity_data.yaml'],
)
async def test_capacities_synchronizer_empty_result(
        taxi_eats_customer_slots,
        yt_apply,
        get_all_places_intervals,
        load_yaml,
):
    expected_data = load_yaml('yt_current_capacity_data.yaml')
    expected_db_state = make_expected_db_state(expected_data)

    await taxi_eats_customer_slots.run_distlock_task(DISTLOCK_TASK_NAME)

    all_places = get_all_places_intervals()
    assert len(expected_db_state) == len(all_places)
    for i, expected in enumerate(expected_db_state):
        utils.compare_place_interval(all_places[i], expected)
