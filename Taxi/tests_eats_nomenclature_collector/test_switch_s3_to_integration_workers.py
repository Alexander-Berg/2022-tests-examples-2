import json

import pytest


@pytest.mark.parametrize(
    'task_type, table_name, filename_tmpl, periodic_name',
    [
        pytest.param(
            'nomenclature',
            'nomenclature_place_tasks',
            'test_nomenclature{}.json',
            'brand-task-result-sender',
            id='nomenclature',
        ),
        pytest.param(
            'price',
            'price_tasks',
            'test_prices{}.json',
            'price-task-result-sender',
            id='price',
        ),
        pytest.param(
            'stock',
            'stock_tasks',
            'test_stocks{}.json',
            'stock-task-result-sender',
            id='stock',
        ),
        pytest.param(
            'availability',
            'availability_tasks',
            'test_availability{}.json',
            'availability-task-result-sender',
            id='availability',
        ),
    ],
)
@pytest.mark.parametrize(
    'switch_settings,'
    'expected_place_ids_in_core,'
    'expected_place_ids_in_iw',
    [
        pytest.param(
            # list of brands, switched to IW
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2', '3', '4'],
                'availability': ['1', '2', '3', '4'],
            },
            # list of expected places in IW
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            id='all_in_core',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': ['2'],
                'price': [],
                'stock': [],
                'availability': [],
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2', '3', '4'],
                'availability': ['1', '2', '3', '4'],
            },
            # list of expected places in IW
            {
                'nomenclature': ['3', '4'],
                'price': [],
                'stock': [],
                'availability': [],
            },
            id='nomenclature_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': ['2'],
                'stock': [],
                'availability': [],
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2'],
                'stock': ['1', '2', '3', '4'],
                'availability': ['1', '2', '3', '4'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': ['3', '4'],
                'stock': [],
                'availability': [],
            },
            id='price_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['2'],
                'availability': [],
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2'],
                'availability': ['1', '2', '3', '4'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['3', '4'],
                'availability': [],
            },
            id='stock_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': [],
                'stock': [],
                'availability': ['2'],
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2', '3', '4'],
                'availability': ['1', '2'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': [],
                'availability': ['3', '4'],
            },
            id='availability_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['2'],
                'availability': ['2'],
            },
            # list of expected places in core
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2'],
                'availability': ['1', '2'],
            },
            # list of expected places in IW
            {
                'nomenclature': [],
                'price': [],
                'stock': ['3', '4'],
                'availability': ['3', '4'],
            },
            id='partially_in_iw',
        ),
        pytest.param(
            # list of brands, switched to IW
            {
                'nomenclature': ['1', '2'],
                'price': ['1', '2'],
                'stock': ['1', '2'],
                'availability': ['1', '2'],
            },
            # list of expected places in core
            {'nomenclature': [], 'price': [], 'stock': [], 'availability': []},
            # list of expected places in IW
            {
                'nomenclature': ['1', '2', '3', '4'],
                'price': ['1', '2', '3', '4'],
                'stock': ['1', '2', '3', '4'],
                'availability': ['1', '2', '3', '4'],
            },
            id='all_in_iw',
        ),
    ],
)
async def test_switch_to_integration_workers(
        taxi_eats_nomenclature_collector,
        load_json,
        mds_s3_storage,
        mockserver,
        pg_cursor,
        testpoint,
        taxi_config,
        task_type,
        table_name,
        filename_tmpl,
        periodic_name,
        # parametrize
        switch_settings,
        expected_place_ids_in_iw,
        expected_place_ids_in_core,
):
    # pylint: disable=unused-variable
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_SWITCH_TO_INTEGRATION_WORKERS': {
                **switch_settings,
            },
        },
    )

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    tasks = []
    for place_id in range(1, 5):
        place_id = str(place_id)
        s3_data = load_json(filename_tmpl.format(''))
        task_filename = filename_tmpl.format(place_id)
        mds_s3_storage.put_object(
            f'some_path/{task_filename}', json.dumps(s3_data).encode('utf-8'),
        )

        assert (
            place_id in expected_place_ids_in_core[task_type]
            or place_id in expected_place_ids_in_iw[task_type]
        )
        if place_id in expected_place_ids_in_core[task_type]:
            s3_path = (
                f'https://eda-integration.s3.mdst.yandex.net/'
                f'some_path/{task_filename}'
            )
        else:
            s3_path = f'some_path/{task_filename}'
        tasks.append(
            _generate_task(
                task_id=task_filename, place_id=place_id, file_path=s3_path,
            ),
        )
    _sql_add_tasks(pg_cursor, table_name, tasks)

    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    if task_type == 'nomenclature':
        # process all brand tasks
        for _ in range(2):
            await taxi_eats_nomenclature_collector.run_periodic_task(
                f'eats-nomenclature-collector_{periodic_name}',
            )
            assert handle_task_finished.has_calls
    else:
        await taxi_eats_nomenclature_collector.run_periodic_task(
            f'eats-nomenclature-collector_{periodic_name}',
        )
        assert handle_task_finished.has_calls

    assert _count_processed(pg_cursor, table_name) == 4


def _generate_task(task_id, place_id, file_path):
    return {
        'id': task_id,
        'place_id': place_id,
        'file_path': file_path,
        'status': 'finished',
    }


def _sql_add_tasks(pg_cursor, table_name, tasks):
    for task in tasks:
        if table_name == 'nomenclature_place_tasks':
            nomenclature_brand_task_id = _get_brand_by_place(
                pg_cursor, task['place_id'],
            )
            pg_cursor.execute(
                f"""
                insert into eats_nomenclature_collector.{table_name} (
                    id,
                    place_id,
                    file_path,
                    status,
                    nomenclature_brand_task_id
                )
                values(
                    %(id)s,
                    %(place_id)s,
                    %(file_path)s,
                    %(status)s,
                    '{nomenclature_brand_task_id}'
                )
                """,
                task,
            )
        else:
            pg_cursor.execute(
                f"""
                insert into eats_nomenclature_collector.{table_name} (
                    id,
                    place_id,
                    file_path,
                    status
                )
                values(
                    %(id)s,
                    %(place_id)s,
                    %(file_path)s,
                    %(status)s
                )
                """,
                task,
            )


def _count_processed(pg_cursor, table_name):
    pg_cursor.execute(
        f'select * from eats_nomenclature_collector.{table_name}',
    )
    rows = pg_cursor.fetchall()
    return sum(row['status'] == 'processed' for row in rows)


def _get_brand_by_place(pg_cursor, place_id):
    pg_cursor.execute(
        f"""
        select brand_id from eats_nomenclature_collector.places
        where id = '{place_id}'
        """,
    )
    return list(pg_cursor)[0]['brand_id']
