import datetime

import pandas as pd

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.couriers_doxgety.experiments.calc_payments import (
    UploadsConfig,
    compute_cost_of_x,
    compute_extra_x,
    count_local_orders,
    group_orders,
    shift_date,
    get_period_length,
    get_orders_targets,
    prepare_payments,
    compute_stats,
)


def test_uploads_config():
    uploads_config = UploadsConfig('2021-04-30', '2021-05-07', 'TICKET-0')

    assert uploads_config.experiment_name_is_relevant('2021-05-06_spb_eda')
    assert uploads_config.experiment_name_is_relevant('2021-04-30_spb_eda')
    assert not uploads_config.experiment_name_is_relevant('2021-05-07_spb_eda')
    assert not uploads_config.experiment_name_is_relevant('')
    assert not uploads_config.experiment_name_is_relevant('abracadabra')

    assert uploads_config.experiment_config_is_relevant(
        {'period': ['2021-04-30', '2021-04-07']},
    )
    assert not uploads_config.experiment_config_is_relevant(
        {'period': ['2021-04-29', '2021-04-06']},
    )
    assert not uploads_config.experiment_config_is_relevant(
        {'period': ['2021-05-01', '2021-05-14']},
    )

    input_configs = [
        {'period': ['2021-04-30', '2021-04-07'], 'ticket': 'TICKET-2'},
        {'period': ['2021-05-01', '2021-05-06'], 'ticket': 'TICKET-2'},
        {'period': ['2021-05-02', '2021-05-07'], 'ticket': 'TICKET-2'},
        {'period': ['2021-05-03', '2021-05-07'], 'ticket': 'TICKET-1'},
    ]
    input_names = [
        '2021-04-30_spb_eda',
        '2021-05-01_spb_eda',
        '2021-05-02_spb_eda',
        '2021-05-03_spb_eda',
    ]

    for exp_name, exp_config in zip(input_names, input_configs):
        uploads_config.add_experiment_config(exp_name, exp_config)

    assert uploads_config.get_tickets_to_put() == {'TICKET-0'}
    expected_input_index = [0, 1, 2, 3]
    i = 0
    for exp_name, config in uploads_config.get_exp_config_iterator('TICKET-0'):
        assert exp_name == input_names[expected_input_index[i]]
        assert config == input_configs[expected_input_index[i]]
        i += 1

    uploads_config = UploadsConfig('2021-04-30', '2021-05-07')

    for exp_name, exp_config in zip(input_names, input_configs):
        uploads_config.add_experiment_config(exp_name, exp_config)

    assert uploads_config.get_tickets_to_put() == {'TICKET-1', 'TICKET-2'}
    expected_input_index = [0, 1, 2]
    i = 0
    for exp_name, config in uploads_config.get_exp_config_iterator('TICKET-2'):
        assert exp_name == input_names[expected_input_index[i]]
        assert config == input_configs[expected_input_index[i]]
        i += 1

    expected_input_index = [3]
    i = 0
    for exp_name, config in uploads_config.get_exp_config_iterator('TICKET-1'):
        assert exp_name == input_names[expected_input_index[i]]
        assert config == input_configs[expected_input_index[i]]
        i += 1


def test_compute_cost_of_x():
    assert (
        compute_cost_of_x(
            test_money=100,
            control_money=0,
            test_x=20,
            control_x=1,
            test_size=100,
            control_size=10,
        )
        == 10
    )


def test_compute_extra_x():
    assert (
        compute_extra_x(test_x=20, control_x=1, test_size=100, control_size=10)
        == 1
    )


def test_count_local_orders():
    orders_input = [
        Record(
            courier_id=1,
            datetime='2021-05-01 16:00:00',
            region_timezone='Asia/Novosibirsk',
        ),
        Record(
            courier_id=1,
            datetime='2021-05-01 17:00:00',
            region_timezone='Asia/Novosibirsk',
        ),
        Record(
            courier_id=1,
            datetime='2021-05-07 17:00:00',
            region_timezone='Asia/Novosibirsk',
        ),
        Record(
            courier_id=2,
            datetime='2021-05-04 23:00:00',
            region_timezone='Europe/Paris',
        ),
        Record(
            courier_id=2,
            datetime='2021-05-05 00:00:00',
            region_timezone='Europe/Paris',
        ),
        Record(
            courier_id=2,
            datetime='2021-05-07 21:00:59',
            region_timezone='Europe/Paris',
        ),
    ]

    local_start_dttm = datetime.datetime.strptime(
        '2021-05-02 00:00:00', '%Y-%m-%d %H:%M:%S',
    )
    local_end_dttm = datetime.datetime.strptime(
        '2021-05-08 00:00:00', '%Y-%m-%d %H:%M:%S',
    )

    expected_output = [
        Record(courier_id=1, date='2021-05-02', orders=1),
        Record(courier_id=2, date='2021-05-05', orders=2),
        Record(courier_id=2, date='2021-05-07', orders=1),
    ]

    output = []

    job = clusters.MockCluster().job()

    count_local_orders(
        job.table('').label('orders_input'), local_start_dttm, local_end_dttm,
    ).put('').label('output')

    job.local_run(
        sources={'orders_input': StreamSource(orders_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


def test_group_orders():
    orders_input = pd.DataFrame(
        columns=['courier_id', 'date', 'orders'],
        data=[
            [1, '2021-05-01', 1],
            [1, '2021-05-02', 2],
            [1, '2021-05-03', 4],
            [1, '2021-05-05', 2],
            [1, '2021-05-07', 5],
            [1, '2021-05-08', 5],
        ],
    )

    period_1 = ['2021-05-02', '2021-05-03']
    expected_output_1 = pd.DataFrame(
        columns=['courier_id', 'orders'], data=[[1, 2]],
    )

    period_2 = ['2021-05-02', '2021-05-07']
    expected_output_2 = pd.DataFrame(
        columns=['courier_id', 'orders'], data=[[1, 8]],
    )

    pd.testing.assert_frame_equal(
        group_orders(orders_input, period_1), expected_output_1,
    )
    pd.testing.assert_frame_equal(
        group_orders(orders_input, period_2), expected_output_2,
    )


def test_shift_date():
    assert shift_date('2021-05-05', 3) == '2021-05-08'
    assert shift_date('2021-05-05', 0) == '2021-05-05'
    assert shift_date('2021-05-05', -2) == '2021-05-03'


def test_get_period_length():
    assert get_period_length(['2021-05-02', '2021-05-07']) == 5
    assert get_period_length(['2021-05-02', '2021-05-02']) == 0


def test_get_orders_targets():
    orders_input = pd.DataFrame(
        columns=['courier_id', 'date', 'orders'],
        data=[
            [1, '2021-05-01', 1],
            [1, '2021-05-02', 2],
            [1, '2021-05-03', 4],
            [1, '2021-05-05', 2],
            [1, '2021-05-07', 5],
            [1, '2021-05-08', 5],
            [2, '2021-05-04', 2],
            [3, '2021-05-08', 4],
        ],
    )

    expected_output = pd.DataFrame(
        columns=['courier_id', 'orders', 'orders_prev'],
        data=[[1, 10, 6], [3, 4, None], [2, None, 2]],
    )

    pd.testing.assert_frame_equal(
        get_orders_targets(orders_input, ['2021-05-06', '2021-05-09']),
        expected_output,
    )


def test_prepare_payments():
    orders_input = pd.DataFrame(
        columns=['courier_id', 'date', 'orders'],
        data=[
            [1, '2021-05-01', 1],
            [1, '2021-05-02', 2],
            [1, '2021-05-03', 4],
            [1, '2021-05-05', 2],
            [1, '2021-05-07', 5],
            [1, '2021-05-08', 5],
            [2, '2021-05-04', 2],
            [3, '2021-05-03', 1],
            [3, '2021-05-04', 4],
            [3, '2021-05-08', 3],
            [3, '2021-05-08', 4],
        ],
    )

    df_input = pd.DataFrame(
        columns=['courier_id', 'orders_target', 'money', 'region_name'],
        data=[
            [1, 15, 500, 'Санкт-Петербург'],
            [2, 4, 300, 'Санкт-Петербург'],
            [3, 7, 400, 'Санкт-Петербург'],
        ],
    )

    config_input = {'region_id': 3, 'period': ['2021-05-06', '2021-05-09']}

    group_name = 'test'
    expected_output = pd.DataFrame(
        columns=[
            'orders_target',
            'group',
            'courier_id',
            'region_name',
            'orders',
            'orders_prev',
            'orders_diff',
            'bonus',
            'hit_target',
            'region_id',
        ],
        data=[
            [15, 'test', 1, 'Санкт-Петербург', 10, 6, 4, 0, 0, 3],
            [4, 'test', 2, 'Санкт-Петербург', 0, 2, -2, 0, 0, 3],
            [7, 'test', 3, 'Санкт-Петербург', 7, 5, 2, 400, 1, 3],
        ],
    )
    pd.testing.assert_frame_equal(
        prepare_payments(df_input, config_input, orders_input, group_name),
        expected_output,
    )

    group_name = 'control'
    expected_output['bonus'] = 0
    expected_output['group'] = 'control'
    pd.testing.assert_frame_equal(
        prepare_payments(df_input, config_input, orders_input, group_name),
        expected_output,
    )


def test_compute_stats():
    cols = [
        'orders_target',
        'group',
        'courier_id',
        'region_name',
        'orders',
        'orders_prev',
        'orders_diff',
        'bonus',
        'hit_target',
        'region_id',
    ]
    test_input = pd.DataFrame(
        columns=cols,
        data=[
            [15, 'test', 1, 'Санкт-Петербург', 10, 6, 4, 0, 0, 3],
            [4, 'test', 2, 'Санкт-Петербург', 0, 2, -2, 0, 0, 3],
            [7, 'test', 3, 'Санкт-Петербург', 7, 5, 2, 400, 1, 3],
            [12, 'test', 4, 'Санкт-Петербург', 14, 10, 4, 300, 1, 3],
        ],
    )
    control_input = pd.DataFrame(
        columns=cols,
        data=[
            [10, 'control', 5, 'Санкт-Петербург', 5, 4, 1, 0, 0, 3],
            [6, 'control', 6, 'Санкт-Петербург', 7, 2, 5, 0, 1, 3],
            [8, 'control', 7, 'Санкт-Петербург', 3, 3, 0, 0, 0, 3],
        ],
    )
    expected_output = pd.DataFrame(
        columns=pd.MultiIndex.from_tuples(
            [
                ('courier_id', 'count'),
                ('hit_target', 'sum'),
                ('bonus', 'sum'),
                ('orders', 'mean'),
                ('orders', 'sum'),
                ('orders_prev', 'mean'),
                ('orders_prev', 'sum'),
                ('orders_diff', 'mean'),
                ('orders_diff', 'sum'),
                ('cpo', ''),
                ('cost_of_order', ''),
                ('extra_orders_prc', ''),
                ('orders_pvalue', ''),
                ('orders_diff_pvalue', ''),
            ],
        ),
        index=['control', 'test'],
        data=[
            [3, 1, 0, 5.0, 15, 3.0, 9, 2.0, 6, 0, 0, 0, 0, 0],
            [
                4,
                2,
                700,
                7.75,
                31,
                5.75,
                23,
                2.0,
                8,
                22.580645,
                63.636364,
                55.0,
                0.475533,
                1.0,
            ],
        ],
    ).rename_axis('group', axis=0)

    pd.testing.assert_frame_equal(
        compute_stats(test_input, control_input), expected_output,
    )
