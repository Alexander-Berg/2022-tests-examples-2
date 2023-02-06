import copy
import datetime

import pytest


from . import test_common


@pytest.fixture(name='mongo_cleaner')
def _mongo_cleaner_fixture(taxi_subvention_order_context, taxi_config):
    class MongoCleaner:
        @staticmethod
        async def set_settings(
                is_enabled=False,
                minimum_seconds_between_cleaner_runs=30,
                max_seconds_since_last_update=86400,
                find_limit=1000,
        ):
            value = {
                'is_enabled': is_enabled,
                'minimum_seconds_between_cleaner_runs': (
                    minimum_seconds_between_cleaner_runs
                ),
                'max_seconds_since_last_update': max_seconds_since_last_update,
                'find_limit': find_limit,
            }
            taxi_config.set_values(
                {'SUBVENTION_ORDER_CONTEXT_MONGO_CLEANER_SETTINGS': value},
            )
            await taxi_subvention_order_context.invalidate_caches()

        @staticmethod
        async def run_once():
            await taxi_subvention_order_context.run_task('mongo-cleaner')

    return MongoCleaner()


@pytest.mark.parametrize(
    'enable_cleaner, max_seconds_since_last_update, expected_size',
    [(False, 300, 3), (True, 10800, 3), (True, 3600, 2), (True, 10, 1)],
)
async def test_task_cleans_necessary_docs(
        mongo_cleaner,
        mongodb,
        replication,
        mocked_time,
        enable_cleaner,
        max_seconds_since_last_update,
        expected_size,
):
    await mongo_cleaner.set_settings(
        is_enabled=enable_cleaner,
        max_seconds_since_last_update=max_seconds_since_last_update,
    )

    now = datetime.datetime(2022, 3, 4, 12)
    mocked_time.set(now)

    new_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    new_data['order_id'] = 'new_order_id'
    new_data['dbid_uuid'] = 'new_dbid_uuid'
    new_data['updated'] = now - datetime.timedelta(minutes=30)
    old_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    old_data['order_id'] = 'old_order_id'
    old_data['dbid_uuid'] = 'old_dbid_uuid'
    old_data['updated'] = now - datetime.timedelta(minutes=120)
    incomplete_data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    incomplete_data['updated'] = now - datetime.timedelta(days=1)
    incomplete_data['value'].pop('tags')

    mongodb.subvention_order_context.insert_many(
        [new_data, old_data, incomplete_data],
    )

    await mongo_cleaner.run_once()
    assert mongodb.subvention_order_context.count() == expected_size


@pytest.mark.now('2020-01-02T00:00:00+00:00')
async def test_replication(mongo_cleaner, mongodb, replication):
    await mongo_cleaner.set_settings(
        is_enabled=True, max_seconds_since_last_update=1,
    )

    data = copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
    mongodb.subvention_order_context.insert_one(data)

    await mongo_cleaner.run_once()

    assert replication.stored == [
        {
            'id': str(data['_id']),
            'data': {
                'order_id_dbid_uuid': 'order_id_dbid_uuid',
                'updated': '2020-01-01T12:00:00+00:00',
                'value': {
                    'driver_point': [37.5, 55.7],
                    'activity_points': 91,
                    'subvention_geoareas': ['geoarea1'],
                    'branding': {'has_sticker': False, 'has_lightbox': False},
                    'tags': ['tag1', 'tag2'],
                    'tariff_class': 'econom',
                    'tariff_zone': 'moscow',
                    'geonodes': 'br_root/br_russia/br_moscow/moscow',
                    'time_zone': 'Europe/Moscow',
                    'unique_driver_id': 'unique_driver_id',
                    'ref_time': '2020-01-01T12:00:00+00:00',
                    'virtual_tags': ['virtual_tag1'],
                },
            },
        },
    ]


async def test_inner_clean_loop(mongo_cleaner, mongodb, replication):
    number_of_db_records = 100
    find_limit = 21
    await mongo_cleaner.set_settings(
        is_enabled=True,
        max_seconds_since_last_update=1,
        find_limit=find_limit,
    )

    mongodb.subvention_order_context.insert_many(
        [
            copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA)
            for _ in range(number_of_db_records)
        ],
    )
    assert mongodb.subvention_order_context.count() == number_of_db_records
    await mongo_cleaner.run_once()
    assert len(replication.stored) == number_of_db_records
    assert mongodb.subvention_order_context.count() == 0
