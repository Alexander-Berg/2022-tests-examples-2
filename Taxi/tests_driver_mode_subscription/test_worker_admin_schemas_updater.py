from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_mode_subscription import mode_rules

_NOW = '2021-04-04T08:00:00+0300'


def _get_all_schema_rows(pgsql, include_hash_in_result: bool = False):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f"""
        SELECT
        name,
        {'hash,' if include_hash_in_result else ''}
        LOWER(compatible_version),
        UPPER(compatible_version)
        FROM config.admin_schemas
        ORDER BY name, compatible_version
        """,
    )
    return list(cursor)


def _get_admin_schema_version(pgsql, include_hash_in_result: bool = False):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f"""
        SELECT
        version
        FROM config.admin_schemas_version
        """,
    )
    rows = list(cursor)
    assert len(rows) == 1
    return rows[0][0]


def _make_insert_admin_schema(
        name: str,
        hash_str: str,
        min_compatible_version: int,
        max_compatible_version: Optional[int],
):
    max_compatible_version_str = (
        'Null'
        if max_compatible_version is None
        else str(max_compatible_version)
    )

    return f"""
        INSERT INTO config.admin_schemas
        (name, schema, hash, compatible_version)
        VALUES ('{name}', '{{}}', '{hash_str}',
        INT4RANGE({min_compatible_version}, {max_compatible_version_str},'[)'))
        """


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[mode_rules.init_admin_schema_version()],
)
@pytest.mark.parametrize(
    'expected_schemas_version, expected_diff_against_service_schemas',
    (
        pytest.param(2, [], id='init service schemas'),
        pytest.param(
            2,
            [('deprecated_name', 1, 2)],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        _make_insert_admin_schema(
                            'deprecated_name', 'some_hash', 1, None,
                        ),
                    ],
                ),
            ],
            id='removed schema',
        ),
        pytest.param(
            2,
            [('active_transport', 0, 1), ('active_transport', 1, 2)],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        _make_insert_admin_schema(
                            'active_transport', 'some_hash_1', 0, 1,
                        ),
                        _make_insert_admin_schema(
                            'active_transport', 'some_hash_2', 1, None,
                        ),
                    ],
                ),
            ],
            id='updated schema',
        ),
    ),
)
@pytest.mark.now(_NOW)
async def test_admin_schemas_updates(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        expected_diff_against_service_schemas: List[Tuple[str, int, None]],
        expected_schemas_version: int,
):
    @testpoint('on-admin-schemas-updater-start')
    def task_start_testpoint(data):
        pass

    @testpoint('admin-schemas-updater-finish')
    def task_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_task('admin-schemas-updater')

    assert task_testpoint.times_called == 1

    current_schema = task_start_testpoint.next_call()['data']['service_schema']

    current_schema_tuples = []

    for name in current_schema:
        current_schema_tuples.append((name, expected_schemas_version, None))

    expected_schemas = (
        expected_diff_against_service_schemas + current_schema_tuples
    )

    actual_schemas = _get_all_schema_rows(pgsql)

    expected_schemas.sort()
    actual_schemas.sort()

    assert actual_schemas == expected_schemas

    actual_schema_version = _get_admin_schema_version(pgsql)
    assert actual_schema_version == expected_schemas_version


@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[mode_rules.init_admin_schema_version()],
)
async def test_preserve_schema_hash(
        taxi_driver_mode_subscription, pgsql, testpoint,
):
    new_schema_name = 'tags'

    @testpoint('on-admin-schemas-updater-start')
    def task_start_testpoint(data):
        current_schema = data['service_schema']
        cursor = pgsql['driver_mode_subscription'].cursor()
        for name, schema in current_schema.items():
            if name == new_schema_name:
                continue

            cursor.execute(
                _make_insert_admin_schema(name, schema['hash'], 1, None),
            )

    @testpoint('admin-schemas-updater-finish')
    def task_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_task('admin-schemas-updater')

    assert task_testpoint.times_called == 1

    actual_rows = _get_all_schema_rows(pgsql, include_hash_in_result=True)

    current_schema = task_start_testpoint.next_call()['data']['service_schema']

    assert len(actual_rows) == len(current_schema)

    for row in actual_rows:
        schema_name = row[0]
        assert schema_name in current_schema

        expected_hash = current_schema[schema_name]['hash']
        expected_min_version = 2 if schema_name == new_schema_name else 1
        expected_max_version = None

        assert row[1] == expected_hash
        assert row[2] == expected_min_version
        assert row[3] == expected_max_version


@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[mode_rules.init_admin_schema_version()],
)
async def test_service_with_old_schema_not_change_schema(
        taxi_driver_mode_subscription, pgsql, testpoint,
):
    old_schema_name = 'tags'

    @testpoint('on-admin-schemas-updater-start')
    def task_start_testpoint(data):
        current_schema = data['service_schema']
        cursor = pgsql['driver_mode_subscription'].cursor()
        old_schema = current_schema[old_schema_name]
        # emulate already applied new schema
        cursor.execute(
            _make_insert_admin_schema(
                old_schema_name, old_schema['hash'], 0, 1,
            ),
        )
        cursor.execute(
            _make_insert_admin_schema(
                old_schema_name, 'some_hash_from_new_service_version', 1, None,
            ),
        )

    @testpoint('admin-schemas-updater-finish')
    def task_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_task('admin-schemas-updater')

    assert task_testpoint.times_called == 1

    actual_rows = _get_all_schema_rows(pgsql, include_hash_in_result=True)

    current_schema = task_start_testpoint.next_call()['data']['service_schema']

    expected_rows = [
        (old_schema_name, current_schema[old_schema_name]['hash'], 0, 1),
        (old_schema_name, 'some_hash_from_new_service_version', 1, None),
    ]

    assert actual_rows == expected_rows
