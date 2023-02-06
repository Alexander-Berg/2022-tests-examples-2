INSERT INTO taxi_db_postgres_atlas_backend.dimension (
    dimension_name,
    description,
    dimension_type
) VALUES
(  -- dimension_id = 1
    'city',
    'Город',
    'STR'
),
(  -- dimension_id = 2
    'time',
    'Время',
    'DATETIME'
),
(  -- dimension_id = 3
    'tariff',
    'Тариф',
    'STR'
),
(  -- dimension_id = 4
    'tags',
    'Тэги',
    'ARRAY_OF_STR'
),
(  -- dimension_id = 5
    'one_more_time',
    'Еще одно время',
    'DATETIME'
),
(  -- dimension_id = 6
    'id',
    'Некий идентификатор',
    'INT'
)
;
