from __future__ import print_function

import pytest


CONFIG1 = dict(
    PREORDER_AVAILABLE_V1_ML_ZONE_RULES={
        'rules': [
            {
                'action': 'permit',
                'affected_tariff_classes': ['vip', 'maybach'],
                'rule_name': 'test',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '07:00:01',
                        'utc_time_end': '12:00:02',
                    },
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '14:00:03',
                        'utc_time_end': '20:00:04',
                    },
                ],
                'zone_polygon': [[0.1, 0.1], [10.1, 0.1], [0.1, 10.1]],
            },
            {
                'action': 'deny',
                'affected_tariff_classes': ['vip'],
                'rule_name': 'test',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '09:00:11',
                        'utc_time_end': '10:00:12',
                    },
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '18:00:13',
                        'utc_time_end': '19:00:14',
                    },
                ],
                'zone_polygon': [[0, 0], [10, 0], [0, 10]],
            },
            {
                'action': 'permit',
                'affected_tariff_classes': ['vip', 'econom'],
                'rule_name': 'test',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '01:00:11',
                        'utc_time_end': '22:00:14',
                    },
                ],
                'zone_polygon': [[50, 50], [60, 50], [50, 60]],
            },
        ],
    },
    PREORDER_AVAILABLE_V1_ML_CONFIG={
        'max_preorder_shift_hours': 36,
        'min_preorder_shift_minutes': 30,
        'model_intervals_min': 10,
        'user_intervals_min': 10,
    },
)

CONFIG2 = dict(
    PREORDER_AVAILABLE_V1_ML_ZONE_RULES={
        'rules': [
            {
                'action': 'permit',
                'affected_tariff_classes': ['vip', 'maybach'],
                'rule_name': 'test',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '14:00:03',
                        'utc_time_end': '04:00:04',
                    },
                ],
                'zone_polygon': [[0.1, 0.1], [10.1, 0.1], [0.1, 10.1]],
            },
        ],
    },
    PREORDER_AVAILABLE_V1_ML_CONFIG={
        'max_preorder_shift_hours': 6,
        'min_preorder_shift_minutes': 30,
        'model_intervals_min': 30,
        'user_intervals_min': 30,
    },
)


@pytest.mark.parametrize(
    'request_file', ['1/request.json', '1/request_noids.json'],
)
@pytest.mark.config(**CONFIG1)
def test_response1(taxi_ml, load_json, request_file):
    request = load_json(request_file)
    response = taxi_ml.post('preorder_available/v1', json=request)
    assert response.status_code == 200

    res = response.json()
    correct_response = load_json('1/response.json')

    assert len(res['allowed_time_info']) == len(
        correct_response['allowed_time_info'],
    )

    tariff_classes = [ti['tariff_class'] for ti in res['allowed_time_info']]
    correct_tariff_classes = [
        ti['tariff_class'] for ti in correct_response['allowed_time_info']
    ]
    assert sorted(tariff_classes) == sorted(correct_tariff_classes)

    time_info = {
        ti['tariff_class']: ti['allowed_time_ranges']
        for ti in res['allowed_time_info']
    }

    correct_time_info = {
        ti['tariff_class']: ti['allowed_time_ranges']
        for ti in correct_response['allowed_time_info']
    }

    assert time_info == correct_time_info


@pytest.mark.parametrize(
    'request_file', ['2/request.json', '2/request_noids.json'],
)
@pytest.mark.config(**CONFIG2)
def test_response2(taxi_ml, load_json, request_file):
    request = load_json(request_file)
    response = taxi_ml.post('preorder_available/v1', json=request)
    assert response.status_code == 200

    res = response.json()
    correct_response = load_json('2/response.json')

    assert len(res['allowed_time_info']) == len(
        correct_response['allowed_time_info'],
    )

    tariff_classes = [ti['tariff_class'] for ti in res['allowed_time_info']]
    correct_tariff_classes = [
        ti['tariff_class'] for ti in correct_response['allowed_time_info']
    ]
    assert sorted(tariff_classes) == sorted(correct_tariff_classes)

    time_info = {
        ti['tariff_class']: ti['allowed_time_ranges']
        for ti in res['allowed_time_info']
    }

    correct_time_info = {
        ti['tariff_class']: ti['allowed_time_ranges']
        for ti in correct_response['allowed_time_info']
    }

    assert time_info == correct_time_info
