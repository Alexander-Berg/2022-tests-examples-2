INSERT INTO taxi_db_postgres_atlas_backend.source_column (
    source_id,
    column_name,
    description,
    db_type,
    native_type,
    expression,
    metadata,
    is_valid
) VALUES
(
    3,
    'record_id',
    'Идентификатор записи',
    'UInt32',
    'INT',
    '',
    '{"Комментарий": {"value": "Здесь будет шутка", "set_by": "someuser"}}',
    True
),
(
    3,
    'city',
    'Город',
    'String',
    'STR',
    '',
    '{}',
    True
),
(
    3,
    'dttm',
    'Время',
    'DateTime',
    'DATETIME',
    '',
    '{"utc_offset": {"value": 3, "set_by": "otheruser"}}',
    True
),
(
    3,
    'dttm_utc',
    'Время UTC',
    'DateTime',
    'DATETIME',
    '{dttm} - 60 * 60 * 3',
    '{"utc_offset": {"value": 0, "set_by": "otheruser"}}',
    True
),
(
    3,
    'quadkey',
    'Идентификатор тайтла',
    'String',
    'STR',
    '',
    '{"length": {"value": 15, "set_by": "thirduser"}}',
    True
),
(
    3,
    'datetime_utc',
    'Старое время',
    'DateTime',
    'DATETIME',
    '{datetime} + 3600',
    '{"utc_offset": {"value": 0, "set_by": "thirduser"}}',
    False
),
(
    3,
    'one_more_datetime',
    'Еще одно время',
    'Nullable(Nothing)',
    'UNSUPPORTED_TYPE',
    'NULL',
    '{"o_key": {"value": "o_value", "set_by": "o_user"}}',
    True
),
(
    4,
    'key',
    'Ключ',
    'String',
    'STR',
    '',
    '{}',
    True
),
(
    4,
    'value',
    'Значение',
    'String',
    'STR',
    '',
    '{}',
    True
)
;
