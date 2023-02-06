INSERT INTO taxi_db_postgres_atlas_backend.metric_instance (
    metric_id,
    source_id,
    expression,
    use_final,
    filters
) VALUES
(
    1,
    3,
    'MAX({id} + {time})',
    false,
    ARRAY['{id} > 100']
),
(
    2,
    3,
    'MIN({id})',
    false,
    ARRAY['{time} >= toDateTime(''2022-01-01 00:00:00'')', '{id} > 50']
),
(
    3,
    1,
    '1',
    false,
    ARRAY[]::text[]
)
;
