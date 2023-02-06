import copy

import pytest


YT_LOGS = []


@pytest.fixture(autouse=True)
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


def round_rec(data):
    if isinstance(data, float):
        return round(data, 3)
    if isinstance(data, list):
        return [round_rec(item) for item in data]
    if isinstance(data, dict):
        res = copy.deepcopy(data)
        for key, value in data.items():
            res[key] = round_rec(value)
        return res
    return data


@pytest.mark.config(
    SURGE_PIPELINE_EXECUTION={
        'UNIFIED_RESOURCES_LOGGING_MODE': 'instance',
        'ENABLE_UNIFIED_STAGE_OUT_LOGGING': True,
    },
)
async def test_nearest_points(taxi_surge_calculator):
    YT_LOGS.clear()
    request = {'point_a': [32.15101, 51.12101], 'classes': ['econom', 'vip']}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.json()

    resource = YT_LOGS[0]['calculation']['$resources']['nearest_point_by_loc']
    resource = round_rec(resource)
    # points surge_points_calculations.json[0,1]
    assert resource == {
        '$instance': {
            'found_value': {
                'avg_ts': -1.0,
                'deviation_from_target_abs_avg': 0.447,
                'deviation_from_target_abs_trend': 0.15,
                'deviation_from_target_abs_values': [0.314, 0.414, 0.614],
                'distance': 1.313,
                'point_b_adj_percentiles': [0.3, 0.4],
                'position_id': 'nearest_by_loc',
                'surge_value_raw': 4.0,
                'surge_value_raw_avg': 2.333,
                'surge_value_raw_trend': 1.5,
                'value_raw_graph': 0,
                'cost': 0,
            },
        },
        '$resource_id': 'nearest_point',
    }

    resource = YT_LOGS[0]['calculation']['$resources']['nearest_point_by_id']
    resource = round_rec(resource)
    # points surge_points_calculations.json[3]
    assert resource == {
        '$instance': {
            'found_value': {
                'avg_ts': 0.0,
                'deviation_from_target_abs_avg': 0.1,
                'deviation_from_target_abs_trend': 0.0,
                'deviation_from_target_abs_values': [0.1],
                'distance': 5.251,
                'point_b_adj_percentiles': [],
                'position_id': 'chosen_id',
                'surge_value_raw': 1.5,
                'surge_value_raw_avg': 1.5,
                'surge_value_raw_trend': 0.0,
                'value_raw_graph': 1.4,
                'cost': 99,
            },
        },
        '$resource_id': 'nearest_point',
    }

    resource = YT_LOGS[0]['calculation']['$resources']['nearest_points_by_loc']
    resource = round_rec(resource)
    assert resource == {
        '$instance': {
            'found_values': {
                'econom': [
                    {
                        'avg_ts': -1.0,
                        'cost': 0.0,
                        'deviation_from_target_abs_avg': 0.447,
                        'deviation_from_target_abs_trend': 0.15,
                        'deviation_from_target_abs_values': [
                            0.314,
                            0.414,
                            0.614,
                        ],
                        'distance': 1.313,
                        'point_b_adj_percentiles': [0.3, 0.4],
                        'position_id': 'nearest_by_loc',
                        'surge_value_raw': 4.0,
                        'surge_value_raw_avg': 2.333,
                        'surge_value_raw_trend': 1.5,
                        'value_raw_graph': 0.0,
                    },
                    {
                        'avg_ts': 0.0,
                        'cost': 99.0,
                        'deviation_from_target_abs_avg': 0.1,
                        'deviation_from_target_abs_trend': 0.0,
                        'deviation_from_target_abs_values': [0.1],
                        'distance': 5.251,
                        'point_b_adj_percentiles': [],
                        'position_id': 'chosen_id',
                        'surge_value_raw': 1.5,
                        'surge_value_raw_avg': 1.5,
                        'surge_value_raw_trend': 0.0,
                        'value_raw_graph': 1.4,
                    },
                ],
                'vip': [
                    {
                        'avg_ts': 0.0,
                        'cost': 0.0,
                        'deviation_from_target_abs_avg': 0.314,
                        'deviation_from_target_abs_trend': 0.0,
                        'deviation_from_target_abs_values': [0.314],
                        'distance': 1.313,
                        'point_b_adj_percentiles': [],
                        'position_id': 'nearest_by_loc',
                        'surge_value_raw': 1.5,
                        'surge_value_raw_avg': 1.5,
                        'surge_value_raw_trend': 0.0,
                        'value_raw_graph': 0.0,
                    },
                ],
            },
        },
        '$resource_id': 'nearest_points',
    }

    resource = YT_LOGS[0]['calculation']['$resources']['nearest_points_by_id']
    resource = round_rec(resource)
    assert resource == {
        '$instance': {
            'found_values': {
                'econom': [
                    {
                        'avg_ts': 0.0,
                        'cost': 99.0,
                        'deviation_from_target_abs_avg': 0.1,
                        'deviation_from_target_abs_trend': 0.0,
                        'deviation_from_target_abs_values': [0.1],
                        'distance': 5.251,
                        'point_b_adj_percentiles': [],
                        'position_id': 'chosen_id',
                        'surge_value_raw': 1.5,
                        'surge_value_raw_avg': 1.5,
                        'surge_value_raw_trend': 0.0,
                        'value_raw_graph': 1.4,
                    },
                    {
                        'avg_ts': 0.0,
                        'cost': 0.0,
                        'deviation_from_target_abs_avg': 0.2,
                        'deviation_from_target_abs_trend': 0.0,
                        'deviation_from_target_abs_values': [0.2],
                        'distance': 11.816,
                        'point_b_adj_percentiles': [],
                        'position_id': 'other_id',
                        'surge_value_raw': 1.5,
                        'surge_value_raw_avg': 1.5,
                        'surge_value_raw_trend': 0.0,
                        'value_raw_graph': 0.0,
                    },
                ],
            },
        },
        '$resource_id': 'nearest_points',
    }
