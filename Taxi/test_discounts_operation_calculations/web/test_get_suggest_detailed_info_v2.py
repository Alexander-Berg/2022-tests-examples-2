import pytest

CONTROL_SHARE = 10


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt2': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
            'payment_types': ['cash', 'applepay', 'googlepay'],
            'classes': ['uberx', 'econom', 'business'],
            'max_absolute_value': 500,
            'disable_by_surge': 1.21,
        },
    },
)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests.sql', 'fill_pg_segment_stats_all.sql'],
)
async def test_get_detailed_info_v2_old(
        web_app_client, set_segments_stats_suggest,
):
    suggest_id = 4
    set_segments_stats_suggest(suggest_id)

    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )
    assert response.status == 200, await response.json()
    content = await response.json()
    assert content == {
        'all_fixed_discounts': [],
        'calc_discounts_params': {
            'budget': pytest.approx(45326175.24480001),
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt2',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                },
            ],
            'max_absolute_value': 500,
            'suggest_id': 4,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': [],
                'discounts_city': 'Москва',
                'max_discount': 50,
                'min_discount': 0,
                'tariffs': ['uberx', 'econom', 'business'],
            },
            'custom_params': [
                {'algorithm_id': 'kt2', 'max_surge': 1.21, 'with_push': False},
            ],
        },
        'multidraft': 'https://ya.ru/42',
        'multidraft_params': {
            'charts': [
                {
                    'algorithm_id': 'kt2',
                    'plot': {
                        'data': [[25, 3.0], [50, 2.0]],
                        'label': 'test_segment',
                        'x_label': 'Цена поездки',
                        'y_label': 'Скидка',
                    },
                },
            ],
            'discount_meta': {
                'kt2': {
                    'budget_spent': pytest.approx(45326175.24480001),
                    'cur_cpeo': pytest.approx(7619.925805238771),
                    'fallback_discount': 0,
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                    'segments_meta': {
                        'control': {
                            'avg_discount': pytest.approx(0.40942267441448776),
                            'budget': pytest.approx(34690759.87200001),
                        },
                        'random': {
                            'avg_discount': pytest.approx(3.066118618310774),
                            'budget': pytest.approx(10635415.372800002),
                        },
                    },
                    'with_push': False,
                },
            },
        },
        'statistics': [
            {
                'algorithm_id': 'kt2',
                'plot': {
                    'data': [
                        [
                            pytest.approx(3239.9408999999996),
                            pytest.approx(318.35294117647055),
                        ],
                    ],
                    'x_label': 'Бюджет',
                    'y_label': 'test_metric_name',
                },
            },
            {
                'algorithm_id': 'kt2',
                'plot': {
                    'data': [
                        [
                            pytest.approx(3239.9408999999996),
                            pytest.approx(149.26556991869967),
                        ],
                    ],
                    'x_label': 'Бюджет',
                    'y_label': 'Цена дополнительного оффера',
                },
            },
        ],
        'status_info': {'status': 'SUCCEEDED'},
        'suggest_version': 1,
    }


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
            'payment_types': ['cash', 'applepay', 'googlepay'],
            'classes': ['uberx', 'econom', 'business'],
            'max_absolute_value': 500,
            'disable_by_surge': 1.21,
        },
    },
)
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_suggests_v2.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
        'fill_pg_segment_stats_all.sql',
    ],
)
async def test_get_detailed_info_v2_calc_segment_stats(web_app_client):
    suggest_id = 1

    response = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )
    assert response.status == 200
    content = await response.json()

    assert content == {
        'all_fixed_discounts': [],
        'calc_discounts_params': {
            'all_fixed_discounts': [
                {'algorithm_id': 'kt', 'fixed_discounts': []},
            ],
            'suggest_id': 1,
        },
        'calc_statistics_params': {
            'common_params': {
                'companies': ['company1', 'company2'],
                'discounts_city': 'test_city',
                'max_discount': 40,
                'min_discount': 0,
                'tariffs': ['uberx', 'econom'],
            },
            'custom_params': [
                {
                    'algorithm_id': 'kt',
                    'max_surge': 1.8,
                    'with_push': True,
                    'fallback_discount': 6,
                },
            ],
        },
        'segments': [
            {
                'algorithm_id': 'kt1',
                'segment_names': ['0', '1', '2', '3', 'control', 'random'],
            },
        ],
        'multidraft': 'https://ya.ru/1123',
        'status_info': {'status': 'NOT_PUBLISHED'},
        'currency_info': {},
        'suggest_version': 2,
        'metric': 'extra_trips',
    }
