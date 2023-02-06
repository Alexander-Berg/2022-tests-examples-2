SKIP_REPLICATION_TABLES = {
    'cargo_finance_claim_estimating_results',
    'claim_segments_journal_v2',
    'claim_segments_journal_v2_buffer',
    'claims_version',
    'claims_version_v2',
    'courier_manual_dispatch',
    'cursors_storage',
    'distlock_callback_broker',
    'distlock_changelog_worker',
    'distlock_claims_cleaner',
    'distlock_periodic_updates',
    'distlock_points_ready_monitor',
    'distlock_replication_monitor',
    'distlock_status_monitor',
    'distlocks',
    'processing_events',
    'replication_monitor_state',
    'schema_version',
}

TABLES_FOR_REPLICATION = {
    'additional_info',
    'carrier_info',
    'change_log',
    'claim_audit',
    'claim_callback',
    'claim_changes',
    'claim_custom_context',
    'claim_estimating_results',
    'claim_features',
    'claim_point_time_intervals',
    'claim_points',
    'claim_segment_points',
    'claim_segment_points_change_log',
    'claim_segments',
    'claim_warnings',
    'claims',
    'claims_c2c',
    'claims_reports',
    'corp_client_names',
    'documents',
    'items',
    'items_exchange',
    'items_fiscalization',
    'matched_cars',
    'matched_items',
    'optimization_tasks',
    'payment_on_delivery',
    'payment_on_delivery_settings',
    'points',
    'points_ready_for_interact_notifications',
    'price_corrections',
    'taxi_order_changes',
    'taxi_performer_info',
}
URL = 'https://wiki.yandex-team.ru'
URI = f'/taxi/backend/logistics/dokumentacija/replikacija-i-arxivirovanie'

ERROR_MESSAGE = f"""
    Если этот тест упал, значит добавили новую таблицу.
    Для нее нужно настроить репликацию/архивацию
    Подробней можно прочитать: {URL}{URI}
"""


async def test_pg_replication(pgsql):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        """
        SELECT tablename FROM pg_catalog.pg_tables
        WHERE schemaname != 'pg_catalog'
            AND schemaname != 'information_schema';
    """,
    )
    assert {item[0] for item in cursor} == {
        *SKIP_REPLICATION_TABLES,
        *TABLES_FOR_REPLICATION,
    }, ERROR_MESSAGE
