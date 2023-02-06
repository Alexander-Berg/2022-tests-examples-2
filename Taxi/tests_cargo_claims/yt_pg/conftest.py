import typing

import pytest

NO_NEED_IN_DENORM = {
    'carrier_info',
    'change_log',
    'claim_callback',
    'claim_segments_journal_v2',
    'claim_segments_journal_v2_buffer',
    'claims_reports',
    'claims_version',
    'claims_version_v2',
    'corp_client_names',
    'cursors_storage',
    'distlock_callback_broker',
    'distlock_changelog_worker',
    'distlock_claims_cleaner',
    'distlock_periodic_updates',
    'distlock_points_ready_monitor',
    'distlock_replication_monitor',
    'distlock_status_monitor',
    'distlocks',
    'optimization_tasks',
    'payment_on_delivery_settings',
    'price_corrections',
    'processing_events',
    'replication_monitor_state',
    'schema_version',
}


TEMPORARY_SKIP_TABLES: typing.Set[str] = set(
    # 'table_name',
)


@pytest.fixture
def denorm_required_tables(pgsql):
    cursor = pgsql['cargo_claims'].cursor()
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


@pytest.fixture
def cut_response():
    def _cut_response(response):
        to_remove = [
            'claim_audit',
            'claim_changes',
            'claim_point_time_intervals',
            'claim_segment_points',
            'claim_segment_points_change_log',
            'documents',
            'matched_items',
            'points_ready_for_interact_notifications',
        ]

        return {
            field: value
            for field, value in response.items()
            if field not in to_remove
        }

    return _cut_response
