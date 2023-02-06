NEW_REQUIRED_FIELDS_ERROR_MESSAGE = """
В таблицу {} добавлены not null поля: {}
Добавления обязательных полей ломает обратную
совместимость с архивными заявками, нужно сделат поля nullable
"""

TABLES_NOT_IN_PG_TABLES_REQUIRED_FIELDS = """
Таблицы {} не найдены в PG_TABLES_REQUIRED_FIELDS
нужно добавить таблицы и их обязательные поля в константу
"""

# Значения полей для таблици в данной константе менять нельзя
# можно только добавляют новые таблицы
PG_TABLES_REQUIRED_FIELDS = {
    'additional_info': {'claim_id', 'id', 'updated_ts', 'claim_uuid'},
    'cargo_finance_claim_estimating_results': {
        'cargo_claim_id',
        'cardstorage_id',
        'id',
        'owner_yandex_uid',
        'claim_uuid',
    },
    'claim_audit': {
        'claim_id',
        'event_time',
        'id',
        'new_status',
        'claim_uuid',
    },
    'claim_changes': {
        'claim_id',
        'created_ts',
        'id',
        'kind',
        'last_known_revision',
        'request_id',
        'status',
        'claim_uuid',
    },
    'claim_custom_context': {
        'claim_id',
        'context',
        'id',
        'updated_ts',
        'claim_uuid',
    },
    'claim_estimating_results': {
        'cargo_claim_id',
        'created_ts',
        'id',
        'status',
        'updated_ts',
        'claim_uuid',
    },
    'claim_features': {'feature_name', 'id', 'updated_ts', 'claim_uuid'},
    'claim_point_time_intervals': {
        'claim_point_id',
        'created_ts',
        'id',
        'type',
        'claim_uuid',
    },
    'claim_warnings': {
        'claim_id',
        'code',
        'id',
        'source',
        'updated_ts',
        'claim_uuid',
    },
    'claim_points': {
        'id',
        'skip_confirmation',
        'type',
        'updated_ts',
        'visit_status',
        'claim_uuid',
    },
    'claim_segment_points': {
        'claim_point_id',
        'created_ts',
        'id',
        'is_fixed_visit_order',
        'revision',
        'segment_id',
        'type',
        'updated_ts',
        'visit_order',
        'visit_status',
        'visited_times',
        'claim_uuid',
    },
    'claim_segment_points_change_log': {
        'event_time',
        'id',
        'new_visit_status',
        'segment_point_id',
        'updated_ts',
        'claim_uuid',
    },
    'claim_segments': {
        'allow_batch',
        'claim_id',
        'claim_uuid',
        'created_ts',
        'dispatch_revision',
        'id',
        'paper_act',
        'perform_order',
        'points_user_version',
        'revision',
        'special_requirements',
        'status',
        'updated_ts',
        'claim_uuid',
    },
    'claims': {
        'created_ts',
        'id',
        'idempotency_token',
        'last_status_change_ts',
        'optional_return',
        'paper_act',
        'revision',
        'skip_act',
        'skip_client_notify',
        'skip_door_to_door',
        'skip_emergency_notify',
        'status',
        'status',
        'updated_ts',
        'uuid_id',
        'version',
    },
    'claims_c2c': {
        'claim_id',
        'created_ts',
        'id',
        'payment_type',
        'updated_ts',
        'yandex_uid',
        'claim_uuid',
    },
    'courier_manual_dispatch': {
        'claim_id',
        'courier_id',
        'id',
        'is_processed',
        'revision',
        'claim_uuid',
    },
    'documents': {
        'claim_id',
        'claim_status',
        'document_type',
        'id',
        'updated_ts',
        'claim_uuid',
    },
    'items': {
        'claim_id',
        'created_ts',
        'delivery_status',
        'droppof_point',
        'id',
        'pickup_point',
        'quantity',
        'title',
        'updated_ts',
        'claim_uuid',
    },
    'items_exchange': {'id', 'quantity', 'updated_ts', 'claim_uuid'},
    'items_fiscalization': {
        'created_ts',
        'id',
        'item_id',
        'updated_ts',
        'claim_uuid',
    },
    'matched_cars': {
        'cargo_claim_id',
        'id',
        'taxi_class',
        'updated_ts',
        'claim_uuid',
    },
    'matched_items': {
        'cargo_claim_id',
        'id',
        'item_id',
        'status',
        'updated_ts',
        'claim_uuid',
    },
    'payment_on_delivery': {
        'claim_point_id',
        'created_ts',
        'id',
        'is_paid',
        'updated_ts',
        'claim_uuid',
    },
    'points': {
        'created_ts',
        'fullname',
        'id',
        'latitude',
        'longitude',
        'updated_ts',
        'claim_uuid',
    },
    'points_ready_for_interact_notifications': {
        'created_ts',
        'id',
        'point_id',
        'updated_ts',
        'claim_uuid',
    },
    'taxi_order_changes': {
        'claim_id',
        'created_ts',
        'id',
        'new_claim_status',
        'reason',
        'updated_ts',
        'claim_uuid',
    },
    'taxi_performer_info': {
        'car_id',
        'car_model',
        'car_number',
        'claim_id',
        'created_ts',
        'driver_id',
        'id',
        'name',
        'park_id',
        'phone_pd_id',
        'taxi_order_id',
        'updated_ts',
        'claim_uuid',
    },
}


async def test_pg_no_new_required_fields(pgsql, denorm_required_tables):
    cursor = pgsql['cargo_claims'].cursor()
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
