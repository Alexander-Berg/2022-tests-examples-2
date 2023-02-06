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

CONFIG3 = dict(
    PREORDER_AVAILABLE_V1_ML_ZONE_RULES={
        'rules': [
            {
                'min_preorder_shift_minutes': 120,
                'action': 'permit',
                'affected_tariff_classes': ['vip', 'maybach'],
                'rule_name': 'test_vip',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '14:00:03',
                        'utc_time_end': '04:00:04',
                    },
                ],
                'zone_polygon': [[0.1, 0.1], [10.1, 0.1], [0.1, 10.1]],
            },
            {
                'max_preorder_shift_hours': 48,
                'action': 'permit',
                'affected_tariff_classes': ['econom'],
                'rule_name': 'test_econom',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '01:00:11',
                        'utc_time_end': '22:00:14',
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
    'request_file, response_file',
    [
        pytest.param(
            '1/request.json',
            '1/response.json',
            marks=pytest.mark.config(**CONFIG1),
            id='1',
        ),
        pytest.param(
            '2/request.json',
            '2/response.json',
            marks=pytest.mark.config(**CONFIG2),
            id='2',
        ),
        pytest.param(
            '3/request.json',
            '3/response.json',
            marks=pytest.mark.config(**CONFIG3),
            id='3 (preorder_shift)',
        ),
    ],
)
async def test_response(
        taxi_umlaas_dispatch, load_json, request_file, response_file,
):
    request = load_json(request_file)
    response = await taxi_umlaas_dispatch.post(
        'umlaas-dispatch/v1/preorder_available', json=request,
    )
    assert response.status_code == 200

    res = response.json()
    correct_response = load_json(response_file)

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
