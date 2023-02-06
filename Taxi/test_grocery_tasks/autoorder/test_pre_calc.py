# pylint: disable=protected-access,invalid-name
import datetime

import pandas as pd
import pytest

from grocery_tasks.autoorder.calc import pre_calc
from grocery_tasks.autoorder.calc.pre_calc import _assortment_set_default_order
from grocery_tasks.autoorder.config import DefaultOrderConfig
from grocery_tasks.autoorder.data_norm import from_yt
from grocery_tasks.autoorder.prepare_data.seasonal import SEASONAL_COLUMNS


def assert_prediction_df_equal(
        result_df: pd.DataFrame, expected_df: pd.DataFrame,
):
    result_df = result_df.set_index(['store_id', 'product_id'])
    result_df.columns = pd.to_datetime(result_df.columns)

    expected_df = expected_df.set_index(['store_id', 'product_id'])
    expected_df.columns = pd.to_datetime(expected_df.columns)

    assert result_df.to_dict() == expected_df.to_dict()


EVENTS_COLUMNS = [
    'store_id',
    'product_id',
    'start_date',
    'ending_date',
    'coef',
]


def test_demand_prediction_apply_events():
    dp_columns = [
        'store_id',
        'product_id',
        '1970-01-01',
        '1970-01-02',
        '1970-01-03',
    ]

    dp_df = pd.DataFrame(
        [
            [100, 1000, 1, 1, 1],
            [100, 1001, 1, 1, 1],
            [200, 1000, 1, 1, 1],
            [200, 1001, 1, 1, 1],
            [300, 1000, 1, 1, 1],
            [300, 1001, 1, 1, 1],
            [111, 1002, 1, 1, 1],
            [222, 1002, 1, 1, 1],
        ],
        columns=dp_columns,
    )

    events_df = pd.DataFrame(
        [
            [100, 1000, '1969-01-01', '1970-01-02', 100],  # ++-
            [100, 1001, '1970-01-02', '1971-01-01', 100],  # -++
            [200, 1000, '1969-01-01', '1971-01-01', 100],  # +++
            [200, 1001, '1970-01-01', '1970-01-03', 100],  # +++
            [0, 0, '1970-01-01', '1970-01-03', 100],  # x
            # Два пересекающихся события для пары товар/лавка 111/1002
            # Результатом должно быть умножение коэффициентов в те дни,
            # когда события накладываются. В данном случае это 1970-01-02
            [111, 1002, '1970-01-01', '1970-01-02', 100],  # ++-
            [111, 1002, '1970-01-02', '1970-01-10', 5],  # -++
            # Два неперсекеющихся события для пары товар/лавка 222/1002
            # Результатом должно быть применение коэффициента для каждого дня,
            # для которого заданы эти события
            [222, 1002, '1970-01-01', '1970-01-01', 10],  # +--
            [222, 1002, '1970-01-02', '1970-01-03', 100],  # -++
        ],
        columns=EVENTS_COLUMNS,
    )

    result_df = pre_calc._demand_prediction_apply_events(
        demand_prediction_df=dp_df, events_df=events_df,
    )
    expected_df = pd.DataFrame(
        [
            [100, 1000, 100, 100, 1],
            [100, 1001, 1, 100, 100],
            [200, 1000, 100, 100, 100],
            [200, 1001, 100, 100, 100],
            [300, 1000, 1, 1, 1],
            [300, 1001, 1, 1, 1],
            [111, 1002, 100, 500, 5],
            [222, 1002, 10, 100, 100],
        ],
        columns=dp_columns,
    )

    assert_prediction_df_equal(result_df=result_df, expected_df=expected_df)


def test_demand_prediction_apply_events_empty_table():
    dp_columns = [
        'store_id',
        'product_id',
        '1970-01-01',
        '1970-01-02',
        '1970-01-03',
    ]

    dp_df = pd.DataFrame(
        [[100, 1000, 1, 1, 1], [200, 1000, 1, 1, 1], [300, 1000, 1, 1, 1]],
        columns=dp_columns,
    )

    events_df = pd.DataFrame([], columns=EVENTS_COLUMNS)

    result_df = pre_calc._demand_prediction_apply_events(
        demand_prediction_df=dp_df, events_df=events_df,
    )
    expected_df = dp_df

    assert_prediction_df_equal(result_df=result_df, expected_df=expected_df)


def test_demand_prediction_seasonal():
    dp_columns = [
        'store_id',
        'product_id',
        '1970-01-01',
        '1970-01-02',
        '1970-01-03',
        '1970-01-04',
        '1970-01-05',
    ]

    dp_df = pd.DataFrame(
        [
            [101, 1001, 1, 1, 1, 1, 1],
            [102, 1002, 1, 1, 1, 1, 1],
            [103, 1003, 1, 1, 1, 1, 1],
            [201, 2001, 1, 1, 1, 1, 1],
            [202, 2002, 1, 1, 1, 1, 1],
            [203, 2003, 1, 1, 1, 1, 1],
            [301, 3001, 1, 1, 1, 1, 1],
            [302, 3002, 1, 1, 1, 1, 1],
            [303, 3003, 1, 1, 1, 1, 1],
            [304, 3004, 1, 1, 1, 1, 1],
        ],
        columns=dp_columns,
    )

    seasonal_df = pd.DataFrame(
        [
            # Формат тестовых данных:
            # product_id, store_id, start_date, ending_date, coef, priority
            # Пример:
            # [100, 1000, '1969-01-01', '1970-01-02', 100, 1]
            # Набор тестовых кейсов 1:
            # Несколько НЕпересекающихся по датам коэффициентов для одной
            # пары лавка-продукт
            #
            # TODO: добавить описание кейсов
            # Кейс 1-1
            [101, 1001, '1969-01-01', '1970-01-03', 10, 1],
            # Кейс 1-2
            [102, 1002, '1970-01-02', '1970-01-04', 10, None],
            # Кейс 1-3
            [103, 1003, '1970-01-05', '1970-01-05', 10, 1],
            # Набор тестовых кейсов 2:
            # Несколько НЕпересекающихся по датам коэффициентов для одной
            # пары лавка-продукт
            #
            # Кейс 2-1: для всех дат есть коэффициенты
            [201, 2001, '1969-01-01', '1970-01-02', 10, 1],
            [201, 2001, '1970-01-03', '1970-02-01', 20, 2],
            # Кейс 2-2: для некотрых дат коэффициентов нет
            [202, 2002, '1969-01-01', '1970-01-02', 10, 1],
            [202, 2002, '1970-01-04', '1970-02-01', 20, 2],
            # Кейс 2-3: несколько точечных интервалов по датам
            [203, 2003, '1970-01-02', '1970-01-02', 10, 1],
            [203, 2003, '1970-01-04', '1970-01-04', 20, 2],
            # Набор тестовых кейсов 3
            # Несколько пересекающихся по датам коэффициентов для одной
            # пары лавка-продукт
            #
            # Кейс 3-1: несколько коэффициентов с разными приоритетами. Для
            # каждой даты выбираем наиболее приоритетный из возможных
            [301, 3001, '1969-01-01', '1970-01-04', 10, 1],
            [301, 3001, '1970-01-03', '1970-02-01', 20, 2],
            [301, 3001, '1970-01-04', '1970-01-04', 30, 3],
            # Кейс 3-2: несколько коэффициентов с одинаковыми приоритетами.
            # При равных приоритетах перемножаем для каждой даты
            # коэффициенты с одинаковым приоритетом
            [302, 3002, '1970-01-03', '1970-02-01', 2, 1],
            [302, 3002, '1969-01-01', '1970-01-04', 10, 1],
            [302, 3002, '1970-01-04', '1970-01-04', 1.5, 1],
            # Кейс 3-3: один из приоритетов не задан. Считаем, что пустой
            # приоритет - самый низкий.
            [303, 3003, '1969-01-01', '1970-01-04', 10, None],
            [303, 3003, '1970-01-02', '1970-02-03', 30, 1],
            [303, 3003, '1970-01-03', '1970-02-01', 20, 3],
            # Кейс 3-4: несколько коэффициентов, но все без приоритетов.
            # Выбираем для каждой даты первый из списка возможных
            [304, 3004, '1969-01-01', '1970-01-02', 10, None],
            [304, 3004, '1970-01-03', '1970-01-04', 2, None],
            [304, 3004, '1970-01-04', '1970-02-01', 30, None],
        ],
        columns=SEASONAL_COLUMNS,
    )

    result_df = pre_calc._demand_prediction_apply_seasonal(
        demand_prediction_df=dp_df, seasonal_df=seasonal_df,
    )
    expected_df = pd.DataFrame(
        [
            [101, 1001, 10, 10, 10, 1, 1],
            [102, 1002, 1, 10, 10, 10, 1],
            [103, 1003, 1, 1, 1, 1, 10],
            [201, 2001, 10, 10, 20, 20, 20],
            [202, 2002, 10, 10, 1, 20, 20],
            [203, 2003, 1, 10, 1, 20, 1],
            [301, 3001, 10, 10, 20, 30, 20],
            [302, 3002, 10, 10, 20, 30, 2],
            [303, 3003, 10, 30, 20, 20, 20],
            [304, 3004, 10, 10, 2, 60, 30],
        ],
        columns=dp_columns,
    )

    assert_prediction_df_equal(result_df=result_df, expected_df=expected_df)


@pytest.mark.parametrize(
    'seasonal_df_columns',
    [
        # if table does not exist, we don't know its schema, so columns of
        # dataframe will be empty
        [],
        # if table is empty, columns will be figured out from schema, but data
        # will be empty
        SEASONAL_COLUMNS,
    ],
)
def test_demand_prediction_seasonal_empty_or_not_exist_table(
        seasonal_df_columns,
):
    """
    Проверяем, что если таблица seasonal пустая или не существует, то скрипт
    выполняется и не изменяет результат прогноза
    """
    dp_columns = [
        'store_id',
        'product_id',
        '1970-01-01',
        '1970-01-02',
        '1970-01-03',
        '1970-01-04',
        '1970-01-05',
    ]

    dp_df = pd.DataFrame(
        [
            [100, 1000, 1, 1, 1, 1, 1],
            [200, 2000, 1, 1, 1, 1, 1],
            [300, 3000, 1, 1, 1, 1, 1],
        ],
        columns=dp_columns,
    )

    seasonal_df = pd.DataFrame([], columns=seasonal_df_columns)

    result_df = pre_calc._demand_prediction_apply_seasonal(
        demand_prediction_df=dp_df, seasonal_df=seasonal_df,
    )
    expected_df = dp_df

    assert_prediction_df_equal(result_df=result_df, expected_df=expected_df)


def test_assortment_append_dolg_pbl():
    assortment_df = pd.DataFrame(
        [
            (110, 1, 110001, 'PBL'),
            (110, 1, 110002, 'PBL'),
            (120, 2, 120001, 'PBL'),
            (777, 3, 777001, 'Хранение'),
            (987, 4, 987001, 'Прямой поставщик'),
        ],
        columns=['supplier_id', 'store_id', 'product_id', 'delivery_type'],
    )

    pbl_df = pd.DataFrame(
        [(110, 1, 777), (120, 2, 777), (120, 3, 777), (120, 4, 777)],
        columns=['supplier_id', 'store_id', 'distribution_center_id'],
    )

    stock_df = pd.DataFrame(
        [
            (777, 110001, 1),
            (777, 110002, 2),
            (777, 120001, 3),
            (777, 777001, 4),
            (77, 987001, -5),
        ],
        columns=['store_id', 'product_id', '1970-01-01'],
    )
    stock_df = stock_df.set_index(['store_id', 'product_id'])

    pbl_distribution_df = pd.DataFrame(
        columns=[
            'supplier_id',
            'product_id',
            'distribution_center_id',
            'fake_distribution_center_id',
        ],
    )

    fake_dc_xor_number = 0  # does not affect

    result_df = pre_calc._assortment_append_dolg_pbl(
        assortment_df=assortment_df,
        pick_by_line_df=pbl_df,
        pbl_distribution_df=pbl_distribution_df,
        stock_df=stock_df,
        fake_dc_xor_number=fake_dc_xor_number,
    )

    expected_df = pd.DataFrame(
        [
            (110, 110001, 1, 'PBL', 110),
            (110, 110002, 1, 'PBL', 110),
            (120, 120001, 2, 'PBL', 120),
            (777, 777001, 3, 'Хранение', 777),
            (987, 987001, 4, 'Прямой поставщик', 987),
            (777, 110001, 1, 'Долг PBL', 110),
            (777, 110002, 1, 'Долг PBL', 110),
            (777, 120001, 2, 'Долг PBL', 120),
        ],
        columns=[
            'supplier_id',
            'product_id',
            'store_id',
            'delivery_type',
            'external_supplier_id',
        ],
    )

    assert result_df.to_dict('records') == expected_df.to_dict('records')


def test_assortment_set_default_order():
    config = DefaultOrderConfig(
        {
            'value': 2,
            'categories_overrides': [
                {'category_name': 'Бананы', 'value': 5},
                {'category_name': 'Виноград', 'value': 7},
            ],
        },
    )
    assortment_df = pd.DataFrame(
        {
            'product_id': [555, 666, 777, 888],
            'quant': [1, 30, 31, 1],
            'supplier_id': [5, 6, 7, 8],
            'store_id': [100, 101, 102, 103],
            'category': ['Бананы', 'Орешки', 'Виноград', 'Голубика'],
        },
    )
    dc_ids = set()
    result_df = _assortment_set_default_order(
        assortment_df=assortment_df,
        dc_ids=dc_ids,
        default_order_config=config,
    )
    expected_df = pd.DataFrame(
        {
            'product_id': [555, 666, 777, 888],
            'quant': [1, 30, 31, 1],
            'supplier_id': [5, 6, 7, 8],
            'store_id': [100, 101, 102, 103],
            'category': ['Бананы', 'Орешки', 'Виноград', 'Голубика'],
            'default_order': [5, 30, 31, 2],
        },
    )
    assert result_df.to_dict() == expected_df.to_dict()


def test_assortment_join_suppliers():
    assortment_df = pd.DataFrame(
        [
            (110, 1, 110001, 'PBL', 110),
            (110, 1, 110002, 'PBL', 110),
            (120, 2, 120001, 'PBL', 120),
            (777, 3, 777001, 'Хранение', 777),
            (987, 4, 987001, 'Прямой поставщик', 987),
            (777, 1, 110001, 'Долг PBL', 110),
            (888, 2, 120001, 'Долг PBL', 120),
            (777, 3, 120001, 'Долг PBL', -1),
        ],
        columns=[
            'supplier_id',
            'store_id',
            'product_id',
            'delivery_type',
            'external_supplier_id',
        ],
    )
    suppliers_df = pd.DataFrame(
        [
            (110, 'внеш. поставщик 1', 5),
            (120, 'внеш. поставщик 2', 3),
            (987, 'внеш. поставщик 3', 0),
        ],
        columns=['supplier_id', 'supplier_name', 'days_before_filling'],
    )
    warehouses_df = pd.DataFrame(
        [(777, 'РЦ 1', 2), (888, 'РЦ 2', 4)],
        columns=['store_id', 'store_name', 'days_before_filling'],
    )

    result_df = pre_calc._assortment_join_suppliers(
        assortment_df=assortment_df,
        suppliers_df=suppliers_df,
        warehouses_df=warehouses_df,
    )

    expected_df = pd.DataFrame(
        [
            (110, 1, 110001, 'PBL', 110, 'внеш. поставщик 1', 5),
            (110, 1, 110002, 'PBL', 110, 'внеш. поставщик 1', 5),
            (120, 2, 120001, 'PBL', 120, 'внеш. поставщик 2', 3),
            (777, 3, 777001, 'Хранение', 777, 'РЦ 1', 2),
            (987, 4, 987001, 'Прямой поставщик', 987, 'внеш. поставщик 3', 0),
            (777, 1, 110001, 'Долг PBL', 110, 'РЦ 1', 5),
            (888, 2, 120001, 'Долг PBL', 120, 'РЦ 2', 3),
            (777, 3, 120001, 'Долг PBL', -1, 'РЦ 1', 0),
        ],
        columns=[
            'supplier_id',
            'store_id',
            'product_id',
            'delivery_type',
            'external_supplier_id',
            'supplier_name',
            'days_before_filling',
        ],
    )

    assert result_df.to_dict('records') == expected_df.to_dict('records')


def test_set_min_supply_date():
    assortment_df = pd.DataFrame(
        [
            (1, 'Рыба', 4, '2020-02-10', '2020-02-12', '2020-02-10'),
            (2, 'Рыба', 4, '2020-02-08', '2020-02-12', '2020-02-08'),
            (3, 'Рыба', 4, '2020-02-07', '2020-02-12', '2020-02-07'),
            (4, 'Мясо', 4, '2020-02-07', '2020-02-12', '2020-02-07'),
            (5, 'Рыба', 0, '2020-02-06', '2020-02-12', '2020-02-12'),
            (6, 'Мясо', 0, '2020-02-06', '2020-02-12', '2020-02-05'),
        ],
        columns=[
            'store_id',
            'category',
            'days_before_filling',
            'purchase_date',
            'open_date',
            'employee_start_date',
        ],
    )
    assortment_df['purchase_date'] = pd.to_datetime(
        assortment_df['purchase_date'],
    )
    assortment_df['open_date'] = pd.to_datetime(assortment_df['open_date'])
    assortment_df['employee_start_date'] = pd.to_datetime(
        assortment_df['employee_start_date'],
    )
    category_exception = set(['Мясо'])
    expected_result_df = pd.DataFrame(
        [
            (1, '2020-02-10'),
            (2, '2020-02-08'),
            (3, '2020-02-08'),
            (4, '2020-02-07'),
            (5, '2020-02-12'),
            (6, '2020-02-05'),
        ],
        columns=['store_id', 'min_supply_date'],
    )
    expected_result_df['min_supply_date'] = pd.to_datetime(
        expected_result_df['min_supply_date'],
    )

    result_df = pre_calc._assortment_set_min_supply_date(
        assortment_df=assortment_df, category_exception=category_exception,
    )[['store_id', 'min_supply_date']]

    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty


def test_stock_subtract_orders_on_the_way():
    # распределительные центры
    dc_ids = {777, 888, 999}

    # дата заказа
    dt = pd.to_datetime('2020-02-12')

    # лавки и скорость поставки на них
    warehouses_df = pd.DataFrame(
        [
            (100, datetime.timedelta(days=0)),
            (101, datetime.timedelta(days=0)),
            (200, datetime.timedelta(days=2)),
        ],
        columns=['store_id', 'delivery_period'],
    )

    # заказы в пути
    orders_on_the_way_df = pd.DataFrame(
        [
            (100, 1, 777, '2020-02-12', 1),
            (100, 1, 777, '2020-02-13', 10),
            (100, 1, 777, '2020-02-14', 100),
            (100, 1, 777, '2020-02-15', 1000),
            (100, 1, 111, '2020-02-12', 1),
            (100, 1, 111, '2020-02-13', 1),
            (100, 1, 111, '2020-02-14', 1),
            (100, 1, 111, '2020-02-15', 1),
            (101, 1, 888, '2020-02-12', 2000),
            (101, 1, 888, '2020-02-13', 200),
            (101, 1, 888, '2020-02-14', 20),
            (101, 1, 888, '2020-02-15', 2),
            (200, 1, 777, '2020-02-12', 3),
            (200, 1, 777, '2020-02-13', 30),
            (200, 1, 777, '2020-02-14', 300),
            (200, 1, 777, '2020-02-15', 3000),
        ],
        columns=['store_id', 'product_id', 'supplier_id', 'date', 'qty'],
    )
    orders_on_the_way_df.date = pd.to_datetime(orders_on_the_way_df.date)

    # остаток на складах
    stock_df = pd.DataFrame(
        [
            (111, 1, 10000),
            (777, 1, 10000),
            (777, 2, 10000),
            (888, 1, 10000),
            (999, 1, 10000),
        ],
        columns=['store_id', 'product_id', 'qty'],
    )

    expected_df = pd.DataFrame(
        [
            (111, 1, 10000),
            (777, 1, 5890),
            (777, 2, 10000),
            (888, 1, 9778),
            (999, 1, 10000),
        ],
        columns=['store_id', 'product_id', 'qty'],
    )

    result_df = pre_calc._stock_subtract_orders_on_the_way(
        stock_df=stock_df,
        orders_on_the_way_df=orders_on_the_way_df,
        warehouses_df=warehouses_df,
        order_date=dt,
        dc_ids=dc_ids,
    )

    assert result_df.to_dict() == expected_df.to_dict()


def test_add_stowage_backlog(get_file_path, open_file):
    with open_file('stowage_backlog/stowage_backlog.csv') as fileobj:
        stowage_backlog_df = from_yt.stowage_backlog(fileobj)
    with open_file('stowage_backlog/otw.csv') as fileobj:
        otw_df = from_yt.orders_on_the_way(fileobj)

    stowage_backlog_df['date'] = stowage_backlog_df['date'].dt.tz_localize(
        None,
    )
    otw_df['date'] = otw_df['date'].dt.tz_localize(None)

    dt = pd.to_datetime('2020-02-12').tz_localize(None)
    weight_products_df = pd.DataFrame()
    common_index = ['store_id', 'product_id', 'date', 'write_off_date']
    pbl_distribution_df = pd.DataFrame(
        [(1212121212, 1212121212, 1212121212, dt, 1)],
        columns=[
            'store_id',
            'supplier_id',
            'product_id',
            'supply_date',
            'qty',
        ],
    )
    common_index = ['store_id', 'product_id', 'date']
    received_df = pre_calc.orders_on_the_way(
        orders_on_the_way_df=otw_df,
        stowage_backlog_df=stowage_backlog_df,
        weight_products_df=weight_products_df,
        pbl_distribution_df=pbl_distribution_df,
        order_date=dt,
    ).set_index(common_index)

    expected_df = pd.read_csv(
        get_file_path('stowage_backlog/result_otw.csv'),
    ).set_index(common_index)
    expected_df['write_off_date'] = pd.to_datetime(
        expected_df['write_off_date'],
    )
    assert len(received_df) == len(expected_df), 'number of rows not equal'
    for ind, expected_row in expected_df.iterrows():
        received_row = received_df.xs(ind)
        assert received_row.to_dict() == expected_row.to_dict(), (
            f'Correct values for row: {ind}',
        )


def test_weight_products():
    weight_products_df = pd.DataFrame(
        [
            (100002, 100001, 0.8),
            (100003, 100001, 1.0),
            (100004, 100001, 1.2),
            (100005, 100001, 1.5),
        ],
        columns=['product_id', 'parent_id', 'avg_weight'],
    )

    dataframe = pd.DataFrame(
        [
            # пример из тикета https://st.yandex-team.ru/LAVKAEFFICIENCY-87
            (100, 100002, 21),
            (100, 100003, 9),
            (100, 100004, 14),
            # случай: продукт и его родитель в датафрейме
            (777, 100002, 3),
            (777, 100005, 9),
            (777, 100001, 2.5),
            # данные для продуктов без родителей не должны меняться
            (100, 100006, 23),
            # продукт - родитель, но детей нет
            (200, 100001, 3.2),
        ],
        columns=['store_id', 'product_id', 'qty'],
    )

    expected_result_df = pd.DataFrame(
        [
            (100, 100001, 42.6),  # 21 * 0.8 + 9 * 1 + 14 * 1.2
            (777, 100001, 18.4),  # 3 * 0.8 + 9 * 1.5 + 2.5 * 1
            (100, 100006, 23),
            (200, 100001, 3.2),
        ],
        columns=['store_id', 'product_id', 'qty'],
    )

    result_df = pre_calc._aggregate_children_products(
        dataframe, weight_products_df,
    )

    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty, difference_df


def test_find_distribution_stores():
    pbl_distribution_df = pd.DataFrame(
        [
            (110001, 110, 777),
            (120002, 120, 777),
            (110002, 110, 888),
            (110002, 100, 888),
        ],
        columns=['product_id', 'supplier_id', 'distribution_center_id'],
    )

    assortment_df = pd.DataFrame(
        [
            (110, 1, 110001, 'PBL'),
            (110, 1, 110002, 'PBL'),
            (110, 2, 110001, 'PBL'),
            (777, 1, 120002, 'Хранение'),
            (120, 2, 120002, 'Прямой поставщик'),
            (777, 3, 120001, 'Долг PBL'),
        ],
        columns=['supplier_id', 'store_id', 'product_id', 'delivery_type'],
    )

    pick_by_line_df = pd.DataFrame(
        [
            (110, 1, 777),
            (110, 2, 777),
            (120, 2, 777),
            (120, 2, 888),
            (100, 10, 888),
        ],
        columns=['supplier_id', 'store_id', 'distribution_center_id'],
    )

    expected_result_df = pd.DataFrame(
        [
            (110001, 110, 777, 1, 'PBL'),
            (110001, 110, 777, 2, 'PBL'),
            (120002, 120, 777, 1, 'Хранение'),
        ],
        columns=[
            'product_id',
            'supplier_id',
            'distribution_center_id',
            'store_id',
            'delivery_type',
        ],
    )

    result_df = pre_calc._find_distribution_stores(
        pbl_distribution_df, assortment_df, pick_by_line_df,
    )
    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty, difference_df


@pytest.mark.now('2020-02-12 06:20:00')
def test_write_off():
    orders_on_the_way_df = pd.DataFrame(
        [
            (200, 1, 777, '2020-02-12', 3),
            (200, 1, 777, '2020-02-13', 30),
            (200, 1, 777, '2020-02-14', 300),
            (200, 1, 777, '2020-02-15', 3000),
            (102, 1, 777, '2020-02-13', 1),
            (102, 1, 777, '2020-02-14', 1),
        ],
        columns=['store_id', 'product_id', 'supplier_id', 'date', 'qty'],
    )
    write_off_wms = pd.DataFrame(
        [
            (102, 1, '2020-02-13', 1),
            (102, 1, '2020-02-14', 1),
            (100, 1, '2020-02-15', 1),
            (101, 1, '2020-02-12', 2000),
            (101, 1, '2020-02-13', 200),
            (101, 1, '2020-02-14', 20),
        ],
        columns=['store_id', 'product_id', 'date', 'qty'],
    )
    orders_on_the_way_df.date = pd.to_datetime(orders_on_the_way_df.date)
    orders_on_the_way_df[
        'write_off_date'
    ] = orders_on_the_way_df.date + datetime.timedelta(days=1)
    write_off_wms.date = pd.to_datetime(write_off_wms.date)
    today_date = datetime.datetime.now()
    result_df = pre_calc.write_offs(
        write_offs_df=write_off_wms,
        weight_products_df=pd.DataFrame(),
        orders_on_the_way_df=orders_on_the_way_df,
        order_date=today_date,
    )

    expected_result_df = pd.DataFrame(
        [
            (100, 1, '2020-02-13', 1.0),
            (102, 1, '2020-02-13', 1.0),
            (102, 1, '2020-02-14', 2.0),
            (102, 1, '2020-02-15', 1.0),
            (101, 1, '2020-02-13', 200.0),
            (101, 1, '2020-02-14', 20.0),
            (200, 1, '2020-02-13', 3.0),
            (200, 1, '2020-02-14', 30.0),
            (200, 1, '2020-02-15', 300.0),
            (200, 1, '2020-02-16', 3000.0),
        ],
        columns=['store_id', 'product_id', 'date', 'qty'],
    )
    expected_result_df.date = pd.to_datetime(expected_result_df.date)
    expected_result_df.set_index(['store_id', 'product_id'], inplace=True)
    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty, difference_df


@pytest.mark.now('2020-02-12 06:20:00')
def test_fill_zero_quants():
    assortment_df = pd.DataFrame(
        [
            (1049, 100004, 60287, 1, 12),
            (1040, 100004, 60287, 0, 12),
            (1757, 100003, 100, 1, 8),
            (1757, 100, 60287, 1, 0),
            (17571, 100, 60287, 1, 1),
            (1757, 100, 71249, 1, 1),
        ],
        columns=['product_id', 'supplier_id', 'store_id', 'order', 'quant'],
    )
    assortment_df_without_zero = pd.DataFrame(
        [
            (1049, 100004, 60287, 1, 12),
            (1040, 100004, 60287, 0, 12),
            (1757, 100003, 100, 1, 8),
            (1757, 100, 60287, 1, 1),
            (17571, 100, 60287, 1, 1),
            (1757, 100, 71249, 1, 1),
        ],
        columns=['product_id', 'supplier_id', 'store_id', 'order', 'quant'],
    )
    pre_calc.fill_zero_quants(
        assortment_warehouses_df=assortment_df,
        order_date=datetime.datetime.now(),
        region_name='russia_center',
    )
    pd.testing.assert_frame_equal(assortment_df, assortment_df_without_zero)
