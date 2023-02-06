NEW_REQUIRED_FIELDS_ERROR_MESSAGE = """
В таблицу {} добавлены not null поля: {}
Добавления обязательных полей ломает обратную
совместимость с архивными заявками, нужно сделат поля nullable
"""

TABLES_NOT_IN_PG_TABLES_REQUIRED_FIELDS = """
Таблицы {} не найдены в PG_TABLES_REQUIRED_FIELDS
нужно добавить таблицы и их обязательные поля в константу
"""

# Значения полей для таблицы в данной константе менять нельзя
# можно только добавляют новые таблицы
PG_TABLES_REQUIRED_FIELDS = {
    'admin_segment_reorders': {
        'created_at',
        'reason',
        'segment_id',
        'updated_ts',
        'waybill_building_version',
    },
    'segment_involved_routers': {
        'priority',
        'router_id',
        'router_source',
        'segment_id',
    },
    'segments': {
        'claim_id',
        'claims_notified_on_orders_changes_version',
        'claims_segment_created_ts',
        'claims_segment_revision',
        'created_ts',
        'is_cancelled_by_user',
        'orders_changes_version',
        'points_user_version',
        'revision',
        'segment_id',
        'status',
        'updated_ts',
        'waybill_building_version',
    },
    'segments_change_log': {'event_time', 'id', 'segment_id', 'updated_ts'},
    'waybill_points': {
        'id',
        'point_id',
        'segment_id',
        'updated_ts',
        'visit_order',
        'waybill_external_ref',
    },
    'waybill_segments': {
        'segment_id',
        'updated_ts',
        'waybill_building_version',
        'waybill_external_ref',
    },
    'waybills': {
        'claims_changes_version',
        'created_ts',
        'external_ref',
        'handle_processing_claims_changes_version',
        'need_commit',
        'orders_notify_claims_changes_version',
        'paper_flow',
        'priority',
        'revision',
        'router_id',
        'special_requirements',
        'status',
        'taxi_order_requirements',
        'updated_ts',
        'waybill_building_deadline',
    },
    'waybills_change_log': {'event_time', 'external_ref', 'id', 'updated_ts'},
}


async def test_pg_no_new_required_fields(pgsql, denorm_required_tables):
    cursor = pgsql['cargo_dispatch'].cursor()
    assert denorm_required_tables == set(PG_TABLES_REQUIRED_FIELDS), (
        TABLES_NOT_IN_PG_TABLES_REQUIRED_FIELDS.format(
            denorm_required_tables - set(PG_TABLES_REQUIRED_FIELDS),
        )
    )
    for table_name, fields in PG_TABLES_REQUIRED_FIELDS.items():
        cursor.execute(
            f"""
                SELECT column_name
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                AND is_nullable = 'NO';
            """,
        )
        table_required_fields = {row[0] for row in cursor}
        assert fields == table_required_fields, (
            NEW_REQUIRED_FIELDS_ERROR_MESSAGE.format(
                table_name, table_required_fields - fields,
            )
        )


async def test_segment_denorm_view(
        pgsql, get_denorm_table_fields, segment_required_tables,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    view_fields = get_denorm_table_fields(cursor, 'segments_denorm_view')

    for table in segment_required_tables:
        assert table in view_fields, (
            f'Table {table} is required for denorm. '
            + 'Add it to segments_denorm_view and do not forget about YT'
        )

    for column in ['segment_id', 'created_ts', 'updated_ts']:
        assert column in view_fields, (
            f'segments_denorm_view is broken; '
            + 'Required column {column} does not exits'
        )


async def test_waybill_denorm_view(
        pgsql, get_denorm_table_fields, waybill_required_tables,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    view_fields = get_denorm_table_fields(cursor, 'waybills_denorm_view')

    for table in waybill_required_tables:
        assert table in view_fields, (
            f'Table {table} is required for denorm. '
            + 'Add it to waybills_denorm_view and do not forget about YT'
        )

    for column in ['external_ref', 'created_ts', 'updated_ts']:
        assert column in view_fields, (
            f'waybills_denorm_view is broken; '
            + 'Required column {column} does not exits'
        )
