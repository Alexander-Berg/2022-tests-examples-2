"""
There is no support for ydb-local in backend-py3.
That is why manual tests were added.

They use personal token from the environment and
run queries in the separate __testing__ folder
on the testing environment in MDB.
"""
import asyncio
import os
import typing as tp

import ydb

from taxi.util import dates

from mayak_inspector.common import constants
from mayak_inspector.common import utils
from mayak_inspector.common.utils import ydb_utils
from mayak_inspector.common.utils import yt_utils
from mayak_inspector.storage.ydb import extractors
from mayak_inspector.storage.ydb import makers
from mayak_inspector.storage.ydb import metrics as metrics_module
from mayak_inspector.storage.ydb import migrations


assert os.getenv('YDB_TOKEN'), 'You need YDB_TOKEN env set to connect'

TESTING_PATH = '__testing__'


async def main():
    # thrown testing database under the bus
    # better to change it for local docker image
    driver_config = ydb.DriverConfig(
        'grpc://ydb-ru-prestable.yandex.net:2135',
        '/ru-prestable/taxiefficiencymayakinspector/testing/mayak_inspector',
        credentials=ydb.construct_credentials_from_environ(),
    )
    print(driver_config)

    with ydb.Driver(driver_config) as driver:
        await asyncio.sleep(1)
        session = driver.table_client.session().create()
        repo = metrics_module.MetricsRepo(context=dict())

        database = os.path.join(driver_config.database, TESTING_PATH)
        path = 'producer/metrics'
        full_path = os.path.join(database, path)

        # test data
        names = ['test', 'a', '2', '1']
        source_id = constants.Sources['yt_metrics'].value
        metrics_rows = [
            {
                'metric': x,
                'metric_order_ids': {'order_ids': [1, 2, 3]},
                'unique_driver_id': x,
            }
            for x in range(16)
        ]
        uuid = utils.make_mayak_entity_uuid(
            original_entity_id=str(0), type_id=0,
        )
        actions_history = [
            makers.ActionValue(
                mayak_action_uuid=1,
                action_type='tagging',
                entity_type='contractor',
                action_entity_id='0',
                rule_name='Cancel',
                zone='spb',
                tariff='comfort',
                status=1,
                mayak_entity_uuid=uuid,
                mayak_import_uuid=1,
                extra=yt_utils.yson_dump(metrics_rows[0]),
                action_params=yt_utils.yson_dump(
                    dict(
                        tariff='low_tariff',
                        message='message',
                        mark=1,
                        author='me',
                        queue='TEST',
                    ),
                ),
                triggered_context=yt_utils.yson_dump(
                    dict(
                        tags=list(),
                        entity=dict(
                            park_driver_profile_ids=list('123'),
                            driver_profiles={'123': '123'},
                        ),
                    ),
                ),
            ),
        ]

        # patch client
        async def execute_query(query_name: str, query_params: tp.Dict):
            query = ydb_utils.load_query(query_name, full_path)
            prepared_query = session.prepare(query)
            result = session.transaction(ydb.SerializableReadWrite()).execute(
                prepared_query, query_params, commit_tx=True,
            )
            print(f'{query_name}: {query_params}')
            if result:
                return result[0].rows
            return []

        repo.execute_query = execute_query

        # apply migrations
        scripts = migrations.MIGRATIONS
        for script in reversed(scripts):
            script.revert(driver, database)
        for script in scripts:
            script.migrate(driver, database)

        # test queries
        imported = await repo.get_import(mayak_import_uuid=1)
        assert imported is None

        await repo.insert_imports(names=names, source_id=source_id)
        imports_gen = repo.get_imports(source_id=source_id)
        imports = [row async for row in imports_gen]
        assert imports

        for row in imports:
            print(row)

        await repo.upsert_metrics(
            mayak_import_uuid=1,
            metrics_rows=metrics_rows,
            original_entity_field='unique_driver_id',
            reason_suffix='_order_ids',
            buckets_num=1,
        )
        await repo.upsert_metrics(
            mayak_import_uuid=1,
            metrics_rows=metrics_rows,
            original_entity_field='unique_driver_id',
            reason_suffix='_order_ids',
        )

        cursor_values = [
            extractors.MetricsCursor(
                left=0,
                right=constants.MAX_UINT64,
                created_at=0,
                mayak_entity_uuid=0,
                is_complete=False,
            ),
        ]
        await repo.create_cursors(mayak_import_uuid=1, values=cursor_values)
        await repo.update_cursor(
            mayak_import_uuid=1, bucket_id=0, value=cursor_values[0],
        )
        cursor = await repo.get_cursor(mayak_import_uuid=1, bucket_id=0)
        assert cursor == cursor_values[0]
        print(cursor)

        page, new_cursor = await repo.get_metrics_with_cursor(
            mayak_import_uuid=1, cursor=cursor,
        )
        assert len(page) == 16
        for row in page:
            print(row)
        assert new_cursor.mayak_entity_uuid == 16815909542856374699

        count = await repo.get_cursor_incomplete_count(mayak_import_uuid=1)
        assert count
        await repo.update_cursor_complete(mayak_import_uuid=1, bucket_id=0)
        count = await repo.get_cursor_incomplete_count(mayak_import_uuid=1)
        assert not count

        entity = await repo.get_entity(uuid)
        assert entity
        print(entity)

        action_id = actions_history[0].mayak_action_uuid
        await repo.upsert_actions_history(action_values=actions_history)
        action = await repo.get_actions_history(mayak_action_uuid=action_id)
        assert action
        print(action)

        last_action = await repo.get_actions_history_last(
            action_type='tagging', entity_type='contractor', entity_id='0',
        )
        assert last_action
        print(last_action)

        await repo.update_actions_history_statuses(
            [dict(mayak_action_uuid=action_id, status=2)],
        )
        actions = [
            action
            async for action in repo.get_batching_actions_cursor(
                mayak_import_uuid=1, status=2, action_type='tagging',
            )
        ]
        assert actions
        print(actions)

        actions = [
            row
            async for row in repo.get_actions_filtered(
                action_type='tagging',
                dtt=dates.localize(),
                entity_type='contractor',
                entity_id='0',
            )
        ]
        assert actions
        print(actions)

        await repo.delete_import(1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
