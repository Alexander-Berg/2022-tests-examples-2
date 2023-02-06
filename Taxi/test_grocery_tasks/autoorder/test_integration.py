# pylint: disable=invalid-name, protected-access
import operator

import pandas as pd
import pytest

from grocery_tasks.autoorder import run_calc
from grocery_tasks.autoorder import run_data_copy


@pytest.mark.translations(wms_items={})
@pytest.mark.now('2020-02-12 06:20:00')
@pytest.mark.yt(
    dyn_table_data=['yt/stores.yaml', 'yt/products.yaml'],
    static_table_data=[
        'yt/prediction.yaml',
        'yt/raw_prediction.yaml',
        'yt/write_offs.yaml',
        'yt/safety_stock_ml.yaml',
        'yt/rotation_info.yaml',
        'yt/rotation_config.yaml',
        'yt/rotation_results.yaml',
        'yt/raw_pim.yaml',
        'yt/raw_seasonal.yaml',
        'yt/seasonal.yaml',
        'yt/weight_products.yaml',
        'yt/stores_clusters.yaml',
        # israel
        'yt/israel/events.yaml',
        'yt/israel/fixed_order.yaml',
        'yt/israel/min_order_sum.yaml',
        'yt/israel/orders_on_the_way.yaml',
        'yt/israel/price_list_of_suppliers.yaml',
        'yt/israel/purchasing_assortment.yaml',
        'yt/israel/quants.yaml',
        'yt/israel/safety_stock.yaml',
        'yt/israel/supplier_relations.yaml',
        'yt/israel/suppliers.yaml',
        'yt/israel/today_schedule.yaml',
        'yt/israel/warehouse_analog.yaml',
        'yt/israel/warehouses.yaml',
    ],
)
@pytest.mark.config(
    GROCERY_AUTOORDER_CONTROL={
        'default_order_coeff': {'value': 3, 'categories_overrides': []},
        'default_shelf_life': 9999,
        'default_expired_count': 0,
        'final_formula': '=need*1',
        'supplier_limits': [
            {
                'supplier_id': 100003,
                'limit': 100000,
                'limit_type': 'proportion',
            },
        ],
        'stowage_backlog': 3,
        'substitution_coeff': 0.7,
        'regions_groups': {
            'test_region_group': {'regions': ['russia_center', 'israel']},
        },
        'regions_list': [
            'england',
            'france',
            'israel',
            'irkutsk',
            'russia_center',
        ],
    },
)
@pytest.mark.config(
    GROCERY_AUTOORDER_MULTIPROCESSING={
        'chunks_count': 500,
        'num_processes': 4,
    },
)
@pytest.mark.config(
    GROCERY_REGIONS_CONTROL={
        'regions': [
            {
                'cities': [{'id': 10393, 'name': 'London'}],
                'jns_notifications': False,
                'name': 'england',
            },
            {'cities': [{'id': 10502, 'name': 'Paris'}], 'name': 'france'},
            {'cities': [{'id': 131, 'name': 'Tel Aviv'}], 'name': 'israel'},
            {'cities': [{'id': 63, 'name': 'irkutsk'}], 'name': 'irkutsk'},
            {
                'cities': [
                    {'id': 193, 'name': 'Voronezh'},
                    {'id': 54, 'name': 'Ekaterinburg'},
                    {'id': 43, 'name': 'Kazan'},
                    {'id': 35, 'name': 'Krasnodar'},
                    {'id': 213, 'name': 'Moscow'},
                    {'id': 47, 'name': 'Nizhniy Novgorod'},
                    {'id': 65, 'name': 'Novosibirsk'},
                    {'id': 39, 'name': 'Rostov-on-Don'},
                    {'id': 2, 'name': 'Saint-Petersburg'},
                    {'id': 172, 'name': 'Ufa'},
                ],
                'jns_notifications': True,
                'name': 'russia_center',
            },
        ],
    },
)
@pytest.mark.config(
    GROCERY_AUTOORDER_TABLES_TO_COPY={
        'default_options': {
            'fallback_allowed': False,
            'required': True,
            'src_type': 'yt',
        },
        'input_tables': {
            'analytics': {
                'default_options': {'src_type': 'yt'},
                'tables': [
                    {
                        'name': 'forecast_new_city',
                        'path_template': (
                            '{yt_external_path}/forecast_new_city'
                        ),  # noqa: E501
                        'required': False,
                    },
                    {
                        'name': 'raw_pim',
                        'path_template': '{yt_eda_dwh_prefix}/dim_lavka_master_category_product/dim_lavka_master_category_product',  # noqa: E501
                        'required': False,
                    },
                    {
                        'fallback_allowed': True,
                        'name': 'raw_prediction',
                        'path_template': '{yt_testing_path}/predictions/catboost/{date}',  # noqa: E501
                    },
                    {
                        'name': 'raw_seasonal',
                        'path_template': '{yt_external_path}/holiday_coeffs',
                        'required': False,
                    },
                    {
                        'name': 'rotation_config',
                        'path_template': (
                            '{yt_eda_analytics_rotation_path}/rotation_config'
                        ),  # noqa: E501
                        'required': False,
                    },
                    {
                        'fallback_allowed': True,
                        'name': 'rotation_info',
                        'path_template': '{yt_eda_analytics_rotation_path}/rotation_results/{date}/ab_split',  # noqa: E501
                        'required': False,
                    },
                    {
                        'fallback_allowed': False,
                        'name': 'rotation_results',
                        'path_template': '{yt_eda_analytics_rotation_path}/rotation_results/{date}/rotation_results',  # noqa: E501
                        'required': False,
                    },
                    {
                        'days_delta': 7,
                        'name': 'sales',
                        'path_template': (
                            '//home/eda-dwh/ods/lavka_1c/order_item/2021-01-01'
                        ),  # noqa: E501
                        'required': False,
                        'src_type': 'clickhouse',
                    },
                    {
                        'name': 'stores_clusters',
                        'path_template': '{yt_eda_dwh_ods_prefix}/stores_clusters/stores_clusters',  # noqa: E501
                    },
                    {
                        'name': 'write_offs',
                        'path_template': (
                            '{lavka_analytics_prefix}/shelf_life_forecast'
                        ),
                        'required': False,
                    },
                ],
            },
            'regional': {
                'default_options': {
                    'path_template': (
                        '{yt_base_path}/{region_name}/{table_name}/{date}'
                    ),  # noqa: E501
                    'src_type': 'yt',
                },
                'russia_center': {
                    'default_options': {
                        'bucket_name': '1c-for-yt',
                        'path_template': (
                            '{table_name}/{table_name}_{date}.csv'
                        ),  # noqa: E501
                        'src_type': 's3',
                    },
                    'override_options': [
                        {
                            'name': 'orders_on_the_way',
                            'path_template': 'ordersOnTheWay/ordersOnTheWay_{date}.csv',  # noqa: E501
                        },
                        {
                            'name': 'pbl_distribution',
                            'path_template': (
                                'PBL_distribution/PBL_distribution_{date}.csv'
                            ),  # noqa: E501
                            'required': False,
                        },
                        {
                            'name': 'pick_by_line',
                            'path_template': 'pbl/pbl_{date}.csv',
                            'required': True,
                        },
                        {'name': 'stock', 'required': True},
                        {
                            'name': 'suppliers',
                            'path_template': 'suppliers.csv',
                        },
                        {
                            'name': 'warehouse_analog',
                            'path_template': 'warehouse_analogs/warehouse_analogs_{date}.csv',  # noqa: E501
                        },
                        {'name': 'warehouses', 'path_template': 'stores.csv'},
                    ],
                },
                'tables': [
                    {'name': 'events', 'required': False},
                    {'name': 'fixed_order', 'required': False},
                    {'name': 'min_order_sum', 'required': False},
                    {'name': 'orders_on_the_way'},
                    {'name': 'pbl_distribution', 'required': False},
                    {'name': 'pick_by_line', 'required': False},
                    {
                        'fallback_allowed': True,
                        'name': 'price_lists_of_suppliers',
                        'path_template': '{yt_base_path}/{region_name}/price_list_of_suppliers/{date}',  # noqa: E501
                        'required': False,
                    },
                    {
                        'fallback_allowed': True,
                        'name': 'purchasing_assortment',
                    },
                    {'fallback_allowed': True, 'name': 'quants'},
                    {'name': 'safety_stock', 'required': False},
                    {'name': 'stock', 'required': False},
                    {'fallback_allowed': True, 'name': 'supplier_relations'},
                    {'name': 'suppliers', 'required': False},
                    {'name': 'today_schedule'},
                    {'name': 'warehouse_analog', 'required': False},
                    {'name': 'warehouses'},
                ],
            },
            'wms': {
                'default_options': {
                    'path_template': (
                        '{yt_replica_path}/postgres/wms/{table_name}'
                    ),
                    'src_type': 'yt',
                },
                'tables': [
                    {'name': 'products', 'required': False},
                    {
                        'name': 'stock_wms',
                        'src_type': 'yql',
                        'src_yt_tables': [
                            {'name': 'products'},
                            {'name': 'stocks'},
                            {'name': 'stores'},
                        ],
                    },
                    {'name': 'stores'},
                    {
                        'max_age': 3,
                        'name': 'stowage_backlog',
                        'required': False,
                        'src_type': 'yql',
                        'src_yt_tables': [
                            {'name': 'orders'},
                            {'name': 'products'},
                            {'name': 'stores'},
                            {'name': 'suggests', 'required': False},
                        ],
                    },
                ],
            },
        },
    },
)
@pytest.mark.config(
    GROCERY_REGIONS_CONTROL={
        'regions': [
            {'cities': [{'id': 10393, 'name': 'London'}], 'name': 'england'},
            {'cities': [{'id': 10502, 'name': 'Paris'}], 'name': 'france'},
            {'cities': [{'id': 131, 'name': 'Tel Aviv'}], 'name': 'israel'},
            {'cities': [{'id': 63, 'name': 'irkutsk'}], 'name': 'irkutsk'},
            {
                'cities': [
                    {'id': 193, 'name': 'Voronezh'},
                    {'id': 54, 'name': 'Ekaterinburg'},
                    {'id': 43, 'name': 'Kazan'},
                    {'id': 35, 'name': 'Krasnodar'},
                    {'id': 213, 'name': 'Moscow'},
                    {'id': 47, 'name': 'Nizhniy Novgorod'},
                    {'id': 65, 'name': 'Novosibirsk'},
                    {'id': 39, 'name': 'Rostov-on-Don'},
                    {'id': 2, 'name': 'Saint-Petersburg'},
                    {'id': 172, 'name': 'Ufa'},
                ],
                'name': 'russia_center',
                'jns_notifications': True,
            },
        ],
    },
)
@pytest.mark.config(
    GROCERY_AUTOORDER_CLIENTS={
        'jns': {
            'api_url': 'https://jns.yandex-team.ru/api',
            'project_name': 'grocery-tasks',
            'request_timeout': 5,
            'server_retry_timeout': 3600,
            'request_retry_num': 5,
            'retry_backoff_coeff': 1.0,
        },
    },
)
@pytest.mark.usefixtures()
async def test_integration(
        load_json,
        cron_context,
        mock_s3_client,
        yt_apply,
        mock_yt,
        mock_yql,
        mock_clickhouse,
        mock_jns,
        yt_client,
        get_file_path,
):
    mock_yt.remount('//home/unittests/replica/postgres/wms/stores')
    mock_yt.remount('//home/unittests/replica/postgres/wms/products')

    region_group = 'test_region_group'
    cron_context.secdist.data['settings_override']['YT_CONFIG']['hahn'][
        'token'
    ] = 'default_key'
    cron_context.secdist.data['settings_override'].setdefault(
        '1C', {'login': '', 'password': ''},
    )
    cron_context.secdist.data['settings_override'].setdefault(
        'woody', {'login': '', 'password': {'israel': ''}},
    )
    await run_data_copy.run(cron_context, region_group)
    await run_calc.run(cron_context, region_group)

    def check_region(result_path: str, region_name: str):
        result = sorted(
            yt_client.read_table(result_path),
            key=operator.itemgetter('warehouse_id', 'supplier_id', 'lavka_id'),
        )

        result_df = pd.DataFrame(result).set_index(
            ['warehouse_id', 'supplier_id', 'lavka_id', 'supply_date'],
        )
        expected_result_df = pd.read_json(
            get_file_path(f'expected/result_{region_name}.json'),
        ).set_index(['warehouse_id', 'supplier_id', 'lavka_id', 'supply_date'])

        round_mapping = {
            'unrounded_order': 2,
            'total_prediction': 2,
            'order_price_with_VAT': 2,
            'order_sum': 2,
            'available_for_sale': 2,
            'quant': 2,
            'need': 2,
            'orders_on_the_way': 2,
            'sales_in_a_week': 2,
            'stock_prediction': 2,
            'safety_stock': 2,
        }

        result_df = result_df.round(round_mapping)
        expected_result_df = expected_result_df.round(round_mapping)
        expected_result_df = expected_result_df.astype({'manager': 'str'})

        for ind, validated_row in expected_result_df.iterrows():
            validated_row = validated_row.to_dict()
            result_row = result_df.xs(ind).to_dict()
            for k, v in validated_row.items():
                if pd.isnull(v):
                    assert pd.isnull(result_row[k]), (
                        f'Correct values for field {k} in row: {ind}',
                    )
                    continue
                assert v == result_row[k], (
                    f'Correct values for field {k} in row: {ind}',
                )

    check_region(
        '//home/unittests/autoorders/russia_center/result/2020-02-12',
        'russia_center',
    )
    check_region(
        '//home/unittests/autoorders/israel/result/2020-02-12', 'israel',
    )
