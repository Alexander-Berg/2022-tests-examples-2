import pytest

from discounts_operation_calculations.internals import statuses


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_last_active_suggest_detailed_info(web_app_client):
    response = await web_app_client.get(
        '/v1/last_active_suggest_id', params={'city': 'Москва'},
    )

    content = await response.json()

    response = await web_app_client.get(
        '/v1/suggest', params={'suggest_id': content['last_suggest_id']},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'algorithms': ['kt2'],
        'budget': pytest.approx(45326175.24480001),
        'calculations': [
            {
                'algorithm_id': 'kt2',
                'fallback_discount': 0,
                'fixed_discounts': [
                    {'discount_value': 0, 'segment': 'control'},
                    {'discount_value': 12, 'segment': 'random'},
                ],
                'plot': [
                    {
                        'data': [
                            [
                                pytest.approx(3239.9408999999996),
                                pytest.approx(318.35294117647055),
                            ],
                        ],
                        'x_label': 'Бюджет',
                        'y_label': 'test_metric_name',
                    },
                    {
                        'data': [
                            [
                                pytest.approx(3239.9408999999996),
                                pytest.approx(149.26556991869967),
                            ],
                        ],
                        'x_label': 'Бюджет',
                        'y_label': 'Цена дополнительного оффера',
                    },
                ],
                'with_push': False,
            },
        ],
        'city': 'Москва',
        'id': 4,
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
        'status': statuses.Statuses.succeeded,
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_detailed_info_with_push(web_app_client):
    response = await web_app_client.get(
        '/v1/suggest', params={'suggest_id': 5},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'id': 5,
        'city': 'Нижний Тагил',
        'multidraft': 'https://ya.ru/110',
        'budget': 69345459.84,
        'algorithms': ['kt6', 'test2'],
        'calculations': [
            {
                'algorithm_id': 'kt6',
                'plot': [
                    {
                        'y_label': 'test_metric_name',
                        'x_label': 'Бюджет',
                        'data': [[3239.9408999999996, 318.35294117647055]],
                    },
                    {
                        'y_label': 'Цена дополнительного оффера',
                        'x_label': 'Бюджет',
                        'data': [[3239.9408999999996, 149.26556991869967]],
                    },
                ],
                'fixed_discounts': [
                    {'segment': 'control', 'discount_value': 6},
                    {'segment': 'random', 'discount_value': 12},
                ],
                'with_push': True,
                'fallback_discount': 3,
            },
        ],
        'multidraft_params': {
            'charts': [
                {
                    'algorithm_id': 'kt6',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[25, 3.0], [50, 2.0]],
                        'label': 'random',
                    },
                },
                {
                    'algorithm_id': 'kt6',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[25, 3.0], [50, 2.0]],
                        'label': 'control',
                    },
                },
                {
                    'algorithm_id': 'test2',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[25, 3.0], [50, 2.0]],
                        'label': 'random',
                    },
                },
                {
                    'algorithm_id': 'test2',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[25, 6.0], [50, 0.0]],
                        'label': 'control',
                    },
                },
                {
                    'algorithm_id': 'kt6fallback',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[50, 3], [700, 3], [750, 0]],
                        'label': 'control',
                    },
                },
                {
                    'algorithm_id': 'kt6fallback',
                    'plot': {
                        'y_label': 'Скидка',
                        'x_label': 'Цена поездки',
                        'data': [[50, 3], [700, 3], [750, 0]],
                        'label': 'random',
                    },
                },
            ],
            'discount_meta': {
                'kt6': {
                    'cur_cpeo': 7619.925805238771,
                    'with_push': True,
                    'budget_spent': 45326175.24480001,
                    'segments_meta': {
                        'random': {
                            'budget': 10635415.372800002,
                            'avg_discount': 3.066118618310774,
                        },
                        'control': {
                            'budget': 34690759.87200001,
                            'avg_discount': 0.40942267441448776,
                        },
                    },
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 6},
                        {'segment': 'random', 'discount_value': 12},
                    ],
                    'fallback_discount': 3,
                },
                'test2': {
                    'cur_cpeo': 11975.623981732246,
                    'with_push': False,
                    'budget_spent': 24019284.595200002,
                    'segments_meta': {
                        'random': {
                            'budget': 7084266.9312,
                            'avg_discount': 4.0566636962837395,
                        },
                        'control': {
                            'budget': 16935017.664,
                            'avg_discount': 0.39973642830739947,
                        },
                    },
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 6},
                        {'segment': 'random', 'discount_value': 12},
                    ],
                    'fallback_discount': None,
                },
                'kt6fallback': {
                    'cur_cpeo': 0,
                    'with_push': True,
                    'budget_spent': 0,
                    'segments_meta': {},
                    'fixed_discounts': [],
                    'fallback_discount': 3,
                },
            },
        },
        'status': 'SUCCEEDED',
    }
