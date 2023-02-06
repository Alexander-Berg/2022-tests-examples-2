import typing

import pytest

NO_NEED_IN_DENORM: typing.Set[str] = {
    'claim_segment_cursor',
    'cursors_storage',
    'distlock_periodic_updates',
    'distlocks',
    'journal_cursor',
    'processed_segments',
    'schema_version',
    'segments_journal',
    'segments_journal_v2',
    'segments_journal_v2_buffer',
    'segments_replication',
    'waybills_journal',
    'waybills_journal_v2',
    'waybills_journal_v2_buffer',
    'waybills_replication',
}

SEGMENT_DENORM_TABLES: typing.Set[str] = {
    'admin_segment_reorders',
    'segment_involved_routers',
    'segments',
    'segments_change_log',
}

WAYBILL_DENORM_TABLES: typing.Set[str] = {
    'waybill_points',
    'waybill_segments',
    'waybills',
    'waybills_change_log',
}


TEMPORARY_SKIP_TABLES: typing.Set[str] = set(
    # 'table_name',
)


@pytest.fixture
def denorm_required_tables(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
            SELECT tablename FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog'
            AND schemaname != 'information_schema';
        """,
    )
    db_tables = {item[0] for item in cursor}
    return db_tables - NO_NEED_IN_DENORM - TEMPORARY_SKIP_TABLES


@pytest.fixture
def segment_required_tables():
    return SEGMENT_DENORM_TABLES


@pytest.fixture
def waybill_required_tables():
    return WAYBILL_DENORM_TABLES


@pytest.fixture
def get_denorm_table_fields():
    def get_table_fields(cursor, table_name: str):
        cursor.execute(
            f"""
                SELECT column_name
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}';
            """,
        )
        table_fields = {row[0] for row in cursor}
        return table_fields

    return get_table_fields
