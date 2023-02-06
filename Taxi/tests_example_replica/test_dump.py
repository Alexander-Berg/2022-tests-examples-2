import datetime
import pathlib

import pytest


DUMP = (
    '{"cursor":"0_1234568_1","lagging_cursor":"0_1549238280_0","size":2}\n'
    + '-1 9 example_220 example_2_main_field4 2 1 -1 1234568 '
    + '1 26 example_1_additional_field9 '
    + 'example_120 example_1_main_field4 2 1 -1 1234567 1 '
)

DUMP_PG = (
    '{"cursor":"2020-06-23T09:56:00+0000_2",'
    + '"lagging_cursor":"2019-02-03T23:58:00+0000_0","size":2}\n'
    + '6 2 1 0 9 example_22 11 some_field21592906160000 6 2 1 0 '
    '9 example_11 11 some_field11592819760000 '
)

CONFIG_ENABLE_DUMP = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': True,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}

CONFIG_DISABLE_DUMP = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}


@pytest.mark.skip('Fix in DIAGNOSTICS-1433')
@pytest.mark.servicetest
@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG_DISABLE_DUMP)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
@pytest.mark.parametrize(
    'dump_prefix, dumper_task_name',
    [
        ('dump-example', 'dumper-example-task'),
        ('dump-example-pg', 'dumper-example-pg-task'),
    ],
)
async def test_dump_store(
        taxi_example_replica,
        build_dir: pathlib.Path,
        taxi_config,
        mocked_time,
        dump_prefix,
        dumper_task_name,
):
    mocked_time.set(datetime.datetime(2019, 2, 4))
    taxi_config.set_values({'API_OVER_DATA_SERVICES': CONFIG_ENABLE_DUMP})
    await taxi_example_replica.tests_control()

    await taxi_example_replica.run_periodic_task(dumper_task_name)
    dump_path = build_dir.joinpath(
        'services/example-replica/testsuite/cache/example-replica',
        '%s-date-2019-02-04T00-00-00-version-1' % dump_prefix,
    )
    taxi_config.set_values({'API_OVER_DATA_SERVICES': CONFIG_DISABLE_DUMP})
    await taxi_example_replica.tests_control()

    assert dump_path.exists()
    dump_path.unlink()
    assert not dump_path.exists()


@pytest.mark.skip('Fix in DIAGNOSTICS-1433')
@pytest.mark.servicetest
@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG_DISABLE_DUMP)
@pytest.mark.filldb(parks='empty')
async def test_dump_load(
        taxi_example_replica, build_dir: pathlib.Path, mocked_time,
):
    dump_dir = build_dir.joinpath(
        'services/example-replica/testsuite/cache/example-replica/',
    )
    dump_path = dump_dir.joinpath(
        'dump-example-date-2019-02-04T00-00-00-version-1',
    )
    if not dump_dir.is_dir():
        dump_dir.mkdir(exist_ok=True, parents=True)

    with dump_path.open('w') as dump:
        dump.write(DUMP)

    await taxi_example_replica.tests_control()
    assert dump_path.exists()
    dump_path.unlink()
    assert not dump_path.exists()

    response = await taxi_example_replica.post(
        'v1/examples/retrieve',
        json={'id_in_set': ['example_1', 'unknown_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples': [
            {
                'revision': '0_1234567_1',
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'data': {
                    'example_main_field': 'example_1_main_field',
                    'example_additional_field': 'example_1_additional_field',
                    'example_object_type_field': {'bool_field': True},
                },
            },
            {'example_id': 'unknown_id', 'example_id_old': 'unknown_id'},
        ],
    }


@pytest.mark.skip('Fix in DIAGNOSTICS-1433')
@pytest.mark.servicetest
@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG_DISABLE_DUMP)
async def test_pg_dump_load(
        taxi_example_replica, build_dir: pathlib.Path, mocked_time,
):
    dump_dir = build_dir.joinpath(
        'services/example-replica/testsuite/cache/example-replica/',
    )
    dump_path = dump_dir.joinpath(
        'dump-example-pg-date-2019-02-04T00-00-00-version-1',
    )
    if not dump_dir.is_dir():
        dump_dir.mkdir(exist_ok=True, parents=True)

    with dump_path.open('w') as dump:
        dump.write(DUMP_PG)

    await taxi_example_replica.tests_control()
    assert dump_path.exists()
    dump_path.unlink()
    assert not dump_path.exists()

    response = await taxi_example_replica.post(
        '/v1/example-pg/retrieve',
        json={'id_in_set': ['example_1', 'example_2']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {
                'data': {
                    'increment': 1,
                    'some_field': 'some_field1',
                    'example_bool_array_field': [True, False],
                    'updated_ts': '2020-06-22T09:56:00.000',
                },
                'example_id': 'example_1',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
            {
                'data': {
                    'increment': 2,
                    'some_field': 'some_field2',
                    'example_bool_array_field': [True, False],
                    'updated_ts': '2020-06-23T09:56:00.000',
                },
                'example_id': 'example_2',
                'revision': '2020-06-23T09:56:00+0000_2',
            },
        ],
    }
