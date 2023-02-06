# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines
import datetime
import typing
from typing import List

import numpy as np
import pandas as pd
import pytest

from grocery_tasks.autoorder.calc import orders_calculator
from grocery_tasks.autoorder.calc import pre_calc

DEFAULTS = {
    'pim': {
        'common_defaults': {
            'shelf_life': 365,
            'days_before_write_off': 3,
            'quant': 1,
            'price': 1.0,
        },
        'items': [
            {'product_id': 1, 'product_name': 'тест Хранение', 'quant': 4},
            {'product_id': 2, 'product_name': 'тест PBL / долг PBL'},
            {
                'product_id': 11,
                'product_name': 'тест Прямой поставщик',
                'price': 10.0,
            },
            {
                'product_id': 12,
                'product_name': 'тест Прямой поставщик',
                'price': 4.5,
            },
            {
                'product_id': 13,
                'product_name': 'тест Прямой поставщик',
                'price': 43,
            },
            {
                'product_id': 14,
                'product_name': 'тест Прямой поставщик',
                'price': 9,
            },
            {
                'product_id': 15,
                'product_name': 'тест Прямой поставщик',
                'quant': 3,
            },
            {
                'product_id': 16,
                'product_name': 'тест Прямой поставщик скоропортящийся товар',
                'shelf_life': 5,
            },
            {
                'product_id': 9,
                'product_name': 'заглушка, не влияет на результат',
            },
            {
                'product_id': 10,
                'product_name': 'default_order',
                'quant': 10,
                'shelf_life': 10,
            },
        ],
    },
    'stock': {
        'items': [
            {'store_id': 100, 'product_id': 1, 'qty': 10.0},
            {'store_id': 200, 'product_id': 1, 'qty': 60},
            {'store_id': 100, 'product_id': 2, 'qty': 4.0},
        ],
    },
    'fixed_order': {
        'items': [
            {
                'store_id': 100,
                'product_id': 9,
                'min_stock': 1,
                'max_stock': 10,
                'order': 100,
            },
        ],
    },
    'otw': {
        'items': [
            {
                'store_id': 100,
                'product_id': 9,
                'date': pd.to_datetime('2020-02-12'),
                'qty': 100,
            },
        ],
    },
    'write_offs': {
        'items': [
            {
                'store_id': 100,
                'product_id': 9,
                'date': '2020-02-12',
                'qty': 100,
            },
        ],
    },
    'min_order_sum': {
        'common_defaults': {'order_trigger': 0.3},
        'items': [
            {
                'supplier_id': 200000,
                'store_id': 5555,
                'increase_order': False,
                'min_order_sum': 30,
            },
            {
                'supplier_id': 200000,
                'store_id': 6666,
                'increase_order': False,
                'min_order_sum': 18,
            },
            {
                'supplier_id': 200000,
                'store_id': 7777,
                'increase_order': False,
                'min_order_sum': 100,
            },
            {
                'supplier_id': 200000,
                'store_id': 8888,
                'increase_order': True,
                'min_order_sum': 100,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 50,
            },
        ],
    },
    # TODO: сделать спрос по умолчанию 0 на месяц вперед
    # для всех складов и продуктов
    'dp_base': {
        'items': [
            {
                'store_id': [1111, 2222, 3333, 9999],
                'product_id': 1,
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 1.0,
            },
            {
                'store_id': 9999,
                'product_id': 2,
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 1.0,
            },
            {
                'store_id': 1111,
                'product_id': 2,
                'start_date': pd.to_datetime('2020-03-01'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 2.0,
            },
            {
                'store_id': 2222,
                'product_id': 2,
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 7.0,
            },
            {
                'store_id': 3333,
                'product_id': 2,
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-02-19'),
                'qty': 2.0,
            },
            {
                'store_id': [5555, 6666, 7777, 8888],
                'product_id': 2,
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 3.0,
            },
            {
                'store_id': [5555, 6666, 7777, 8888, 9999],
                'product_id': [11, 12, 13, 14],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 1.0,
            },
            {
                'store_id': [9999],
                'product_id': [15],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 6.0,
            },
            {
                'store_id': [9999],
                'product_id': [16],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 11.0,
            },
            {
                'store_id': [2222],
                'product_id': [10],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 16.0,
            },
            {
                'store_id': [3333],
                'product_id': [10],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 27.0,
            },
            {
                'store_id': [4444],
                'product_id': [10],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 3.0,
            },
            {
                'store_id': [5555],
                'product_id': [10],
                'start_date': pd.to_datetime('2020-02-17'),
                'end_date': pd.to_datetime('2020-03-20'),
                'qty': 3.0,
            },
            {
                'store_id': [9876],
                'product_id': [11, 12, 13, 14, 15],
                'start_date': pd.to_datetime('2020-02-12'),
                'end_date': pd.to_datetime('2020-03-12'),
                'qty': 1.0,
            },
        ],
    },
    'assortment_base': {
        'common_defaults': {
            'store_name': 'test store',
            'supplier_name': 'test supplier',
            'category': 'test category',
            'subcategory': 'test subcategory',
            'manager': 'test manager',
            'supplier_quant': 1,
            # TODO: вычислять default_order
            # c помощью _assortment_set_default_order
            'default_order': 0.0,
            'safety_stock': 0.0,
            'min_supply_date': pd.to_datetime('2020-02-11'),
            'delivery_period': datetime.timedelta(days=0),
            'groupby_columns': 1,
        },
        'items': [
            {
                'supplier_id': 100000,
                'store_id': 100,
                'product_id': 1,
                'delivery_type': 'Хранение',
            },
            {
                'supplier_id': 100,
                'store_id': [1111, 2222, 3333, 9999],
                'product_id': 1,
                'delivery_type': 'Хранение',
            },
            {
                'supplier_id': 100,
                'store_id': list(range(1111, 10000, 1111)),
                'product_id': 2,
                'delivery_type': 'Долг PBL',
            },
            {
                'supplier_id': 100000,
                'store_id': list(range(1111, 10000, 1111)),
                'product_id': 2,
                'delivery_type': 'PBL',
            },
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1015)) + [2222, 3333, 4444],
                'product_id': 10,
                'delivery_type': 'Долг PBL',
                'default_order': 10,
            },
            {
                'supplier_id': 100000,
                'store_id': [1001, 1008, 1010, 1011, 5555],
                'product_id': 10,
                'delivery_type': 'Прямой поставщик',
                'default_order': 10,
            },
            {
                'supplier_id': 200000,
                'store_id': [5555, 6666, 7777, 8888, 9999],
                'product_id': list(range(11, 17)),
                'delivery_type': 'Прямой поставщик',
            },
            {
                'supplier_id': 200000,
                'store_id': [9876],
                'product_id': list(range(11, 17)),
                'delivery_type': 'Прямой поставщик',
                'min_supply_date': pd.to_datetime('2020-03-11'),
            },
        ],
    },
    'orders_to_redistribute': {
        'items': [
            {
                'order_id': 'заглушка',
                'supplier_id': 100,
                'product_id': 9,
                'qty': 100,
            },
        ],
    },
    'pick_by_line': {
        'items': [
            {'store_id': -1, 'supplier_id': -1, 'distribution_center_lag': 1},
        ],
    },
}


def _get_defaults(data_name: str) -> typing.Optional[pd.DataFrame]:
    data_defaults = DEFAULTS.get(data_name)
    if data_defaults is None:
        return None

    data_defaults = typing.cast(typing.Dict['str', typing.Any], data_defaults)
    default_df = pd.DataFrame(data_defaults['items'])
    for column in default_df.columns:
        default_df = default_df.explode(column)

    common_defaults = data_defaults.get('common_defaults')
    if common_defaults is None:
        return default_df

    for col, value in common_defaults.items():
        if col in default_df.columns:
            default_df[col] = default_df[col].fillna(value)
        else:
            default_df[col] = value

    return default_df


def _get_update(update: List[dict]):
    update_df = pd.DataFrame(update)
    for column in update_df.columns:
        update_df = update_df.explode(column)
    return update_df


def get_data(data_name, update: List[dict] = None, index=None):
    default_df = _get_defaults(data_name)

    if update is None:
        return default_df

    update_df = _get_update(update)

    if default_df is None:
        return update_df

    result_df = update_df.append(default_df).drop_duplicates(
        subset=index, keep='first',
    )

    return result_df


def generate_schedule_df(schedule_base, assortment_df, pim_df, order_date):
    schedule_df = get_data('schedule', schedule_base)

    schedule_df['supply_date_lists'] = schedule_df['supply_date_lists'].apply(
        tuple,
    )

    schedule_df['order_date'] = order_date
    schedule_df['supply_dates'] = schedule_df['supply_date_lists']

    schedule_df = schedule_df.explode('supply_dates')
    schedule_df['supply_date'] = schedule_df['supply_dates']
    schedule_df['next_supply_date'] = schedule_df.groupby(
        ['supplier_id', 'store_id', 'product_id', 'supply_date_lists'],
    )['supply_dates'].transform('shift', -1)
    schedule_df = schedule_df.dropna(subset=['next_supply_date'])
    schedule_df = schedule_df.reset_index()
    schedule_df['order_date'] = pd.to_datetime(schedule_df['order_date'])
    schedule_df['supply_date'] = pd.to_datetime(schedule_df['supply_date'])
    schedule_df['next_supply_date'] = pd.to_datetime(
        schedule_df['next_supply_date'],
    )
    schedule_df['date_of_delivery_to_dc'] = pd.NaT
    schedule_df = schedule_df[
        [
            'supplier_id',
            'store_id',
            'product_id',
            'order_date',
            'supply_date',
            'next_supply_date',
            'date_of_delivery_to_dc',
        ]
    ]

    return schedule_df


def generate_assortment_df(pim_df, min_order_sum_df, dc_ids):
    dataframe = get_data('assortment_base')
    dataframe = pd.merge(dataframe, pim_df, on='product_id', how='inner')

    dataframe['store_type'] = 'lavka'
    dataframe.loc[dataframe.store_id.isin(dc_ids), 'store_type'] = 'dc'

    dataframe['unpacking_period'] = datetime.timedelta(days=0)
    dataframe.loc[
        dataframe.store_id.isin(dc_ids), 'unpacking_period',
    ] = datetime.timedelta(days=1)

    dataframe['prepare_period'] = datetime.timedelta(days=1)

    dataframe['supplier_type'] = 'external_supplier'
    dataframe.loc[dataframe.supplier_id.isin(dc_ids), 'supplier_type'] = 'dc'

    dataframe['correction_group'] = dataframe.apply(
        pre_calc._get_correction_groups, axis='columns',
    )

    dataframe = pre_calc._assortment_add_suppliers_as_stores(
        assortment_df=dataframe,
    )

    dataframe = pre_calc._assortment_add_min_order_sum(
        assortment_df=dataframe, min_order_sum_df=min_order_sum_df,
    )

    return dataframe.drop_duplicates(
        subset=['supplier_id', 'store_id', 'correction_group', 'product_id'],
        keep='first',
    )


def generate_dp_df(update: List[dict] = None):
    dp_df = get_data('dp_base', update)

    result_df = dp_df

    result_df['date'] = result_df.apply(
        lambda row: pd.date_range(
            start=row['start_date'],
            end=row['end_date'],
            closed='left',
            freq='D',
        ),
        axis='columns',
    )
    result_df = result_df.explode('date')
    result_df = result_df.drop_duplicates(
        subset=['store_id', 'product_id', 'date'],
    )
    result_df = result_df[['store_id', 'product_id', 'date', 'qty']]

    return result_df.set_index(['store_id', 'product_id'])


def generate_test_data(raw_test_data, param_list):
    prepared_test_data = []
    for test_name, test_params in raw_test_data.items():
        test_params['test_name'] = test_name
        test_data = []
        for param in param_list:
            test_data.append(test_params.get(param))
        prepared_test_data.append(tuple(test_data))
    return prepared_test_data


# TODO: we can move it to test_orders_calculator/test_data.hjson file when
# Arcadia Tier 0 will be done. Now we can't import hjson
TEST_DATA_DICT = {
    # ТЕСТИРОВАНИЕ ПРЯМЫХ ПОСТАВОК
    'DirectDelivery1': {
        # Тестирование мин суммы
        # increase_order = False:
        #   5555: orders_price_sum < min_order_sum -> заказы 0
        #   6666: orders_price_sum = min_order_sum -> заказ по потребности
        #   7777: orders_price_sum > min_order_sum -> заказ по потребности
        #
        # increase_order = True:
        # zero_order_limit = min_order_sum * order_trigger
        #   8888: orders_price_sum < zero_order_limit -> заказ 0
        #   9999: min_order_sum > orders_price_sum >= zero_order_limit
        #     -> перерасчеты 3 раза, пока не выбьем мин сумму
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 5555,
                'product_id': 11,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
            {
                'supplier_id': 200000,
                'store_id': 5555,
                'product_id': 12,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
            {
                'supplier_id': 200000,
                'store_id': 6666,
                'product_id': 12,
                'supply_date_lists': [('2020-02-13', '2020-02-17')],
            },
            {
                'supplier_id': 200000,
                'store_id': 7777,
                'product_id': 13,
                'supply_date_lists': [('2020-02-14', '2020-02-17')],
            },
            {
                'supplier_id': 200000,
                'store_id': 8888,
                'product_id': 14,
                'supply_date_lists': [('2020-02-14', '2020-02-17')],
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date_lists': [('2020-02-14', '2020-02-17')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 5555,
                'product_id': 11,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 5555,
                'product_id': 12,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 6666,
                'product_id': 12,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 7777,
                'product_id': 13,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 8888,
                'product_id': 14,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 5.0,
            },
        ],
    },
    # За 15 дней не успеваем добиться цены заказа min_order_sum
    # используем перераспределние вверх для цен
    'DirectDelivery2': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 67.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 402.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.01,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 1000,
            },
        ],
    },
    'DirectDelivery3': {
        'schedule_base': [
            # обнуляемся тк не хватает до order_trigger * min_order_sum
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 12,
                'supply_date_lists': [('2020-02-14', '2020-02-17')],
            },
            # заказ как есть тк цена заказа больше мин суммы
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 13,
                'supply_date_lists': [('2020-02-16', '2020-02-18')],
            },
            #  несколько товаров в одной поставке, доводим до мин сумммы
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date_lists': [('2020-02-13', '2020-02-16')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 12,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 13,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 2.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 24.0,
            },
        ],
    },
    'DirectDelivery4': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date_lists': [
                    ('2020-02-13', '2020-02-14', '2020-02-15'),
                ],
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date_lists': [('2020-02-13', '2020-02-16')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 30.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.1,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 50,
            },
        ],
    },
    'DirectDelivery5': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date_lists': [
                    ('2020-02-13', '2020-02-15', '2020-02-17'),
                ],
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date_lists': [
                    ('2020-02-13', '2020-02-14', '2020-02-15', '2020-02-17'),
                ],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 18.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 24.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.1,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 50,
            },
        ],
    },
    # случай, когда общая цена заказа уменьшшается при перезаказе
    # из-за otw, тем не менее мы уже раз превысили zero_order_limit,
    # поэтому по итогу должны дополнить до минсуммы
    'DirectDelivery6': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date_lists': [('2020-02-14', '2020-02-17')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 5.0,
            },
        ],
        'otw': [
            {
                'store_id': 9999,
                'product_id': 11,
                'date': pd.to_datetime('2020-02-17'),
                'qty': 3,
            },
        ],
    },
    # Товар 15 имеет срок годности год.
    # Товар 16 скоропортящийся (shelf_life - days_before_write_off = 2),
    # поэтому максимальный период перерасчета равен 2.
    # До исправления https://st.yandex-team.ru/LAVKAEFFICIENCY-362
    # периоды перерасчета для разных товаров разъезжались.
    'DirectDelivery7': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [15, 16],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 18.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 16,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 33.0,
            },
        ],
    },
    # за один перерасчет превышаем мин сумму (orders_price_sum = 145 > 100)
    # уменьшаем заказы, чтобы приблизиться как можно ближе к min_order_sum
    'DirectDelivery8': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [11, 12, 13, 14, 15],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 12,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 13,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 2.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 12.0,
                'rounded_order_from_dc': 6.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.1,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 100,
            },
        ],
    },
    # Превышаем мин сумму с первого раза  без перезаказов (72.5 > 50),
    # поэтому дополнительно НЕ приближаем order_prices_sum к мин сумме.
    'DirectDelivery9': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [11, 12, 13, 14, 15],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [11, 12, 13, 14],
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 1.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 6.0,
                'rounded_order_from_dc': 6.0,
            },
        ],
    },
    # Не можем выбрать мин сумму за период перерасчета (1087.5 < 1100)
    # Пропорционально увеличиваем заказы (order_prices_sum: 1087.5 -> 1157),
    # затем приближаем order_prices_sum к мин сумме (1157 -> 1130.5)
    'DirectDelivery10': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [11, 12, 13, 14, 15],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 15.0,
                'rounded_order_from_dc': 15.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 12,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 15.0,
                'rounded_order_from_dc': 15.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 13,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 15.0,
                'rounded_order_from_dc': 16.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 15.0,
                'rounded_order_from_dc': 15.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 90.0,
                'rounded_order_from_dc': 90.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.01,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 1100,
            },
        ],
    },
    # тестирование order_trigger = 0.0
    # склад 9876 еще не открыт, поэтому, изначальный заказ равен 0.0
    # поэтому order_prices_sum = zero_order_limit = 0.0
    # по текущей логике пытаемся добрать до мин суммы, но все перезаказы
    # также равны 0.0, поэтому финальные заказы равны 0.0
    'DirectDelivery11': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9876,
                'product_id': [11, 12, 13, 14, 15],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9876,
                'product_id': [11, 12, 13, 14, 15],
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.0,
                'supplier_id': 200000,
                'store_id': 9876,
                'increase_order': True,
                'min_order_sum': 100,
            },
        ],
    },
    # тестирование order_trigger = 0.0
    # первичный заказ равен 0.0, это значит, что
    # order_prices_sum = min_order_sum, поэтому за 2 перерасчета
    # добиваем до мин суммы и перераспределяем заказы вниз
    'DirectDelivery12': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [11, 12, 13],
                'supply_date_lists': [('2020-02-13', '2020-02-14')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 11,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 12,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 13,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 2.0,
                'rounded_order_from_dc': 2.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.0,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 100,
            },
        ],
        'stock': [{'store_id': 9999, 'product_id': [11, 12, 13], 'qty': 2.0}],
    },
    # товар 16 имеет срок годности 2 дня, из-за него не можем делать перезаказы
    # order_price_sum < zero_order_limit (112 < 500), поэтому обнуляемся
    'DirectDelivery13': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [14, 15, 16],
                'supply_date_lists': [('2020-02-13', '2020-02-19')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [14, 15, 16],
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.5,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 1000,
            },
        ],
    },
    # товар 16 имеет срок годности 2 дня, из-за него не можем делать перезаказы
    # order_price_sum > zero_order_limit (112 > 100),
    # поэтому перераспределяем заказы ввверх
    'DirectDelivery14': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [14, 15, 16],
                'supply_date_lists': [('2020-02-13', '2020-02-19')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 6.0,
                'rounded_order_from_dc': 54.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 36.0,
                'rounded_order_from_dc': 324.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 16,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 22.0,
                'rounded_order_from_dc': 197.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.1,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 1000,
            },
        ],
    },
    # товар 16 имеет срок годности 2 дня, из-за него не можем делать перезаказы
    # order_price_sum = zero_order_limit (112 = 112),
    # поэтому перераспределяем заказы вверх
    'DirectDelivery15': {
        'schedule_base': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': [14, 15, 16],
                'supply_date_lists': [('2020-02-13', '2020-02-19')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 14,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 6.0,
                'rounded_order_from_dc': 54.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 15,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 36.0,
                'rounded_order_from_dc': 324.0,
            },
            {
                'supplier_id': 200000,
                'store_id': 9999,
                'product_id': 16,
                'supply_date': '2020-02-13',
                'theoretic_rounded_order': 22.0,
                'rounded_order_from_dc': 197.0,
            },
        ],
        'min_order_sum': [
            {
                'order_trigger': 0.112,
                'supplier_id': 200000,
                'store_id': 9999,
                'increase_order': True,
                'min_order_sum': 1000,
            },
        ],
    },
    # ТЕСТИРОВАНИЕ ХРАНЕНИЯ
    # на РЦ есть остаток, но его не хватает на обеспечение лавок
    # все реальные поставки на лавки снабжаются из остатка на рц на 12ое
    # нужно 7, есть только 3
    # заказ на РЦ высчитывается исходя из теоретических поставок на лавки
    'Hranenie1': {
        'schedule_base': [
            {
                'supplier_id': 100000,
                'store_id': 100,
                'product_id': 1,
                'supply_date_lists': [['2020-02-13', '2020-02-15']],
            },
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date_lists': [['2020-02-16', '2020-02-20']],
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 1,
                'supply_date_lists': [['2020-02-14', '2020-02-16']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 1,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100000,
                'store_id': 100,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 5.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 2.0,
            },
            # должно было было привезтись 2,
            # но остатков на РЦ до первой поставки на РЦ не хватило
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 1,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 1, 'qty': 3.0}],
        'pim': [
            {
                'product_id': 1,
                'shelf_life': 365,
                'days_before_write_off': 3,
                'quant': 1,
            },
        ],
    },
    # вывоз остатков РЦ на лавки с округлением вниз
    # товар при прочих равных распределяется сначала
    # на лавки с меньшим номером
    'Hranenie2': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': [1111, 2222, 3333],
                'product_id': 1,
                'supply_date_lists': [['2020-02-13', '2020-02-17']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 1,
                'supply_date_lists': [['2020-02-13', '2020-02-22']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 12.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 1, 'qty': 17.0}],
    },
    'Hranenie_2postavki_na_odny_lavky': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date_lists': [
                    ['2020-02-13', '2020-02-14', '2020-02-15'],
                ],
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 1,
                'supply_date_lists': [['2020-02-16', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 1,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 2.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 1, 'qty': 10.0}],
        'pim': [{'product_id': 1, 'quant': 1}],
    },
    'Hranenie_odinochnoe': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date_lists': [('2020-02-13', '2020-02-15')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 1,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 8.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 1, 'qty': 8.0}],
        'pim': [{'product_id': 1, 'quant': 1000}],
    },
    # ТЕСТИРОВАНИЕ ДОЛГА  PBL
    # должны по-другому распределять
    'PBL1': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': [5555, 6666, 7777, 8888],
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-17']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 5555,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 12.0,
            },
            {
                'supplier_id': 100,
                'store_id': 6666,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 8.0,
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 8.0,
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 8.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 36.0}],
        'pim': [
            {
                'product_id': 2,
                'shelf_life': 365,
                'days_before_write_off': 3,
                'quant': 4,
            },
        ],
    },
    # максимальный период расчета долга
    'PBL2': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 20.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 20.0}],
    },
    # перераспределение с долга PBL, округленного вниз на  PBL
    #       долг PBL:     |+++++++[+/-]--------------|
    #       PBL:          |-------[-/+]|
    #       долг PBL:     |+++++++[+/-]|
    #       PBL:          |-------[-/+]|
    #       долг PBL:     |+|+++++[+/-]|
    #       PBL:             |----|
    #       долг PBL:     |++++|++[+/-]
    #       PBL:                 |[-/+]|
    'PBL3': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-29']],
            },
            {
                'supplier_id': 100000,
                'store_id': 1111,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-17']],
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-17']],
            },
            {
                'supplier_id': 100000,
                'store_id': 2222,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-17']],
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 3333,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-16']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-15']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-16', '2020-02-17']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 1111,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 24.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 2222,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 7.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 3333,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 1.0,
            },
        ],
        'stock': [
            {'store_id': 100, 'product_id': 2, 'qty': 34.0},
            {'store_id': 1111, 'product_id': 2, 'qty': 5.0},
        ],
    },
    #       долг PBL:     |+++++|++++
    #       долг PBL:     |++|+++++++
    #            PBL:     |----------+++++|
    'PBL4': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-03-12']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-03-16']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 21.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1111,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 13.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 7.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 34.0}],
    },
    #       долг PBL:     |++|++++
    #       PBL:          |-|
    'PBL5': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-15']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 4.0}],
    },
    #       долг PBL:     |++|++++
    #       PBL:          |-------++|
    'PBL6': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 1.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 4.0}],
    },
    #       долг PBL:     |++|++++++++
    #       PBL:             |-----|--++++|
    'PBL7': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [
                    ['2020-02-14', '2020-02-16', '2020-02-20'],
                ],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 3.0,
            },
        ],
    },
    # сейчас работает неправильно
    #       долг PBL:     |++|+++++
    #       PBL:       |??---------|
    'PBL8': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-15']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,  # 1.0,
            },
        ],
    },
    #       долг PBL:     |+++++-------|
    #       PBL:       |++------++++|
    'PBL9': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-20']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-19']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 2.0,
            },
        ],
    },
    #       долг PBL:     |+++|++++
    #       PBL:       |++---------++++|
    'PBL10': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-15', '2020-02-16']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-20']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
            },
        ],
    },
    #       долг PBL:     |++++|+++++++++
    #       PBL:                 |----|
    'PBL11': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-16']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
        ],
    },
    #       долг PBL:     |++++|++++++
    #       PBL:                 |----+++|
    'PBL12': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-16', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 1.0,
            },
        ],
    },
    # долг PBL в прироритете, пока не вывезли все с РЦ,
    # по PBL ничего не везем
    #       долг PBL:          |+++++++++++----|
    #       PBL:                  |----|
    'PBL13': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-18']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-15']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
        ],
    },
    # Несмотря на то, что уже открылся заказ с внешнего поставщика,
    # долг PBL везем приоритетом
    #       долг PBL:          |+++++++++----------|
    #       PBL:                    |----+++++|
    'PBL14': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-19']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-15', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 1.0,
            },
        ],
    },
    # Комплексный тест PBL / долга PBL
    # разнообразные даты поставки по долгу PBL (в случае разных регионов)
    # https://st.yandex-team.ru/LAVKAEFFICIENCY-306
    #       только долг PBL
    #       5555 долг PBL:       |+|++[+/-]
    #
    #       только PBL
    #       6666 PBL:      |++++++|
    #
    #       долг PBL налезает на PBL
    #       2222 долг PBL:     |+|++[+/-]
    #       2222 PBL:             |-[-/+]+++++|
    #
    #       долг PBL не пересекается с PBL
    #       3333 долг PBL: |+|++[+/-]
    #       3333 PBL:                |++|
    #
    #       несколько поставок по PBL
    #       7777 долг PBL:    |+|+ +[+/-]
    #       7777 PBL:         |-|-|-[-/+]
    #
    #       PBL начинается раньше долга
    #       8888 долг PBL:      |+|++[+/-]
    #       8888 PBL:        |++-----[-/+]++|
    #
    #       перераспределенный вниз заказ по долгу PBL довозится по PBL
    #       9999 долг PBL:   |+|++[+/-]
    #       9999 PBL:        |----[-/+]|
    'PBL15': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 5555,
                'product_id': 2,
                'supply_date_lists': [['2020-02-18', '2020-02-19']],
            },
            {
                'supplier_id': 100000,
                'store_id': 6666,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-17']],
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 2,
                'supply_date_lists': [['2020-02-16', '2020-02-17']],
            },
            {
                'supplier_id': 100000,
                'store_id': 2222,
                'product_id': 2,
                'supply_date_lists': [['2020-02-18', '2020-02-25']],
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100000,
                'store_id': 3333,
                'product_id': 2,
                'supply_date_lists': [['2020-02-17', '2020-02-19']],
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date_lists': [['2020-02-15', '2020-02-16']],
            },
            {
                'supplier_id': 100000,
                'store_id': 7777,
                'product_id': 2,
                'supply_date_lists': [
                    ['2020-02-15', '2020-02-16', '2020-02-17', '2020-02-19'],
                ],
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date_lists': [['2020-02-16', '2020-02-17']],
            },
            {
                'supplier_id': 100000,
                'store_id': 8888,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-18']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-15']],
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-14', '2020-02-18']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 5555,
                'product_id': 2,
                'supply_date': '2020-02-18',
                'rounded_order_from_dc': 12.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 6666,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 12.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 26.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 2222,
                'product_id': 2,
                'supply_date': '2020-02-18',
                'rounded_order_from_dc': 37.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 6.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 3333,
                'product_id': 2,
                'supply_date': '2020-02-17',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 11.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-17',
                'rounded_order_from_dc': 1.0,
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date': '2020-02-16',
                'rounded_order_from_dc': 12.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 8888,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 3.0,
            },
            {
                'supplier_id': 100000,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-14',
                'rounded_order_from_dc': 1.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 70.0}],
    },
    # расчет долга PBL заканчивается с окончанием срока годности товара
    'PBL16': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 170.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 280.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 450.0}],
    },
    # ТЕСТИРОВАНИЕ ЗАКАЗА ПО УМОЛЧАНИЮ
    # склады 1000 - 1014 с нулевым средним прогнозом
    # склады 2222, 3333, 4444, 5555 с ненулевым средним прогнозом
    # склады 1004 - 1009 имеют поставки в пути
    # склады 1000 - 1006 имеют ненулевые остатки в начале расчета
    'DefaultOrder1': {
        # товар по долгу PBL распределяется за 1 день
        # на склад 4444 везется товар по потребности
        # на складе 1000, должен привезтись заказ по умолчанию,
        # но товара не хватает и он везется с приоритетом склада,
        # у которого есть прогноз
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': [1000, 4444],
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 1000,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
            },
            {
                'supplier_id': 100,
                'store_id': 4444,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 14.0}],
    },
    'DefaultOrder2': {
        # товар по долгу PBL распределяется за 1 день
        # на склады 2222, 3333 туда везется товар по потребности
        # на складах 1000 - 1009, на которые хватает, заказ по умолчанию
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1010)) + [2222, 3333],
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1006)),
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1006,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 7.0,
            },
            {
                'supplier_id': 100,
                'store_id': list(range(1007, 1010)),
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 20.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 30.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 117.0}],
    },
    'DefaultOrder3': {
        # товар по долгу PBL распределяется за 5 дней
        # и заказ в конце округляется вниз
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1010)) + [2222, 3333],
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1010)),
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 72.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 130.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 302.0}],
    },
    'DefaultOrder4': {
        # товар по долгу PBL не распределяется за период распределения (7 дней)
        # и заказ в конце округляется вверх пропорционально
        # max(dp_mean, default_order)
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1010)) + [2222, 3333],
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': list(range(1000, 1008)),
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 60.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1008,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 33.0,
            },
            {
                'supplier_id': 100,
                'store_id': 1009,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 190.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 310.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 1023.0}],
    },
    'DefaultOrder5': {
        # долг PBL распределяется за 3 дня
        # при перерасчете заказа на новые склады 1010 - 1014 всегда
        # получаем заказ по умолчанию
        # на склады 2222 и 3333 с прогнозом товар распределяется по потребнсти
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': list(range(1010, 1015)) + [2222, 3333],
                'product_id': 10,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': list(range(1010, 1015)),
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
            {
                'supplier_id': 100,
                'store_id': 2222,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 43.0,
            },
            {
                'supplier_id': 100,
                'store_id': 3333,
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 80.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 10, 'qty': 173.0}],
    },
    'DefaultOrder6': {
        # Проверка логики включения заказа по умолчанию:
        #   склад 1001: нулевой заказ т.к. ненулевые остатки в начале расчета
        #   склад 1008: нулевой заказ т.к. ненулевые товары в пути
        #   склад 1011: нулевой заказ т.к. ненулевые остатки + товары в пути
        #   склад 1010: первый заказ по умолчанию, последующие - нулевые
        #   склад 5555: заказываем квант, т.к. ненулевой средний спрос и
        #       утренний сток нулевой, см. LAVKAEFFICIENCY-364
        'schedule_base': [
            {
                'supplier_id': 100000,
                'store_id': [1001, 1008, 1011, 5555],
                'product_id': 10,
                'supply_date_lists': [['2020-02-15', '2020-02-16']],
            },
            {
                'supplier_id': 100000,
                'store_id': [1010],
                'product_id': 10,
                'supply_date_lists': [
                    ['2020-02-13', '2020-02-15', '2020-02-16', '2020-02-20'],
                ],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100000,
                'store_id': [1001, 1008, 1011],
                'product_id': 10,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': [1010],
                'product_id': 10,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 10.0,
            },
            {
                'supplier_id': 100000,
                'store_id': [1010],
                'product_id': 10,
                'supply_date': ['2020-02-15', '2020-02-16'],
                'rounded_order_from_dc': 0.0,
            },
            {
                'supplier_id': 100000,
                'store_id': [5555],
                'product_id': 10,
                'supply_date': '2020-02-15',
                'rounded_order_from_dc': 10.0,
            },
        ],
        'otw': [
            {
                'store_id': [1008, 1011],
                'product_id': 10,
                'date': [
                    pd.to_datetime('2020-02-13'),
                    pd.to_datetime('2020-02-17'),
                ],
                'qty': 100,
            },
        ],
        'stock': [
            {'store_id': [1001], 'product_id': 10, 'qty': 5},
            {'store_id': [1011], 'product_id': 10, 'qty': 5},
        ],
    },
    # товар приходит на рц сегодня, потребности одинаковые
    # распределяется по приоритету лавок [округление вниз]
    'PBLdistribution1': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
                'order_id': '',
            },
            {
                'supplier_id': 100,
                'store_id': 8888,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
                'order_id': '',
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 7.0}],
        'orders_to_redistribute': [
            {
                'order_id': 'PBLdistribution1',
                'supplier_id': 100,
                'product_id': 2,
                'redistr_qty': 7.0,
            },
        ],
    },
    # товар приходит на рц сегодня, потребности разные
    # распределяется по потребностям и приоритету лавок
    'PBLdistribution2': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 7.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 2.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
                'order_id': '',
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 0.0,
                'order_id': '',
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 9.0}],
        'orders_to_redistribute': [
            {
                'order_id': 'PBLdistribution1',
                'supplier_id': 100,
                'product_id': 2,
                'redistr_qty': 9.0,
            },
        ],
    },
    # товар приходит на рц сегодня, потребности разные
    # есть другие остатки [пока что без otw]
    # распределяется по потребностям и приоритету лавок
    'PBLdistribution3': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date_lists': [['2020-02-13', '2020-02-14']],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 4.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 1.0,
                'order_id': 'PBLdistribution1',
            },
            {
                'supplier_id': 100,
                'store_id': 7777,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 3.0,
                'order_id': '',
            },
            {
                'supplier_id': 100,
                'store_id': 9999,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 1.0,
                'order_id': '',
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 9.0}],
        'orders_to_redistribute': [
            {
                'order_id': 'PBLdistribution1',
                'supplier_id': 100,
                'product_id': 2,
                'redistr_qty': 5.0,
            },
        ],
    },
    # долг PBL без PBL
    # TODO: запускать тест в отсутствие ассортимента кроме как из расписания
    'DolgPBL1': {
        'schedule_base': [
            {
                'supplier_id': 100,
                'store_id': 5555,
                'product_id': 2,
                'supply_date_lists': [('2020-02-13', '2020-02-29')],
            },
            {
                'supplier_id': 100,
                'store_id': 6666,
                'product_id': 2,
                'supply_date_lists': [('2020-02-13', '2020-02-29')],
            },
        ],
        'expected_result': [
            {
                'supplier_id': 100,
                'store_id': 5555,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 9.0,
            },
            {
                'supplier_id': 100,
                'store_id': 6666,
                'product_id': 2,
                'supply_date': '2020-02-13',
                'rounded_order_from_dc': 9.0,
            },
        ],
        'stock': [{'store_id': 100, 'product_id': 2, 'qty': 18.0}],
    },
}

PARAM_LIST = [
    'test_name',
    'schedule_base',
    'expected_result',
    'stock',
    'pim',
    'orders_to_redistribute',
    'min_order_sum',
    'otw',
    'dp_base',
    'pick_by_line',
]


@pytest.mark.parametrize(
    ', '.join(PARAM_LIST), generate_test_data(TEST_DATA_DICT, PARAM_LIST),
)
def test_orders_calculator(
        test_name,
        schedule_base,
        expected_result,
        stock,
        pim,
        orders_to_redistribute,
        min_order_sum,
        otw,
        dp_base,
        pick_by_line,
):
    dc_ids = [100, 200]
    start_date = pd.to_datetime('2020-02-12')

    pim_df = get_data('pim', pim, ['product_id'])

    stock_df = get_data('stock', stock, ['store_id', 'product_id'])
    stock_df = stock_df.set_index(['store_id', 'product_id'])
    stock_df = stock_df.sort_index()

    orders_to_redistribute_df = get_data(
        'orders_to_redistribute', orders_to_redistribute,
    )

    pick_by_line_df = get_data('pick_by_line', pick_by_line)

    fixed_order_df = get_data('fixed_order')

    otw_df = get_data('otw', otw)
    otw_df.set_index(['store_id', 'product_id'], inplace=True)

    write_offs_df = get_data('write_offs')

    dp_df = generate_dp_df(dp_base)

    min_order_sum_df = get_data('min_order_sum', min_order_sum)

    assortment_df = generate_assortment_df(
        pim_df=pim_df, min_order_sum_df=min_order_sum_df, dc_ids=dc_ids,
    )

    today_schedule_df = generate_schedule_df(
        assortment_df=assortment_df,
        schedule_base=schedule_base,
        pim_df=pim_df,
        order_date=start_date,
    )

    calculator = orders_calculator.OrdersCalculator(
        assortment_df=assortment_df,
        stock_df=stock_df,
        fixed_order_df=fixed_order_df,
        today_schedule_df=today_schedule_df,
        pim_df=pim_df,
        otw_df=otw_df,
        dp_df=dp_df,
        write_offs_df=write_offs_df,
        safety_stock_ml_df=pd.DataFrame(
            columns=[
                'store_id',
                'product_id',
                'supply_period',
                'safety_stock_ml',
            ],
        ),
        orders_to_redistribute_df=orders_to_redistribute_df,
        pick_by_line_df=pick_by_line_df,
        start_date=start_date,
    )

    result_df = pd.DataFrame(calculator.calc())
    result_df['order_id'] = result_df.order_id.fillna('')

    expected_result_df = get_data('expected_result', expected_result)

    columns = list(
        np.intersect1d(result_df.columns, expected_result_df.columns),
    )
    result_df = result_df[columns]

    expected_result_df = expected_result_df[columns]
    for column in expected_result_df.columns:
        expected_result_df[column] = expected_result_df[column].astype(
            result_df[column].dtypes.name,
        )

    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty, difference_df
