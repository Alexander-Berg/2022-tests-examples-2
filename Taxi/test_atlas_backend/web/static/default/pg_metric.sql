INSERT INTO taxi_db_postgres_atlas_backend.metric (
    ru_name,
    en_name,
    ru_description,
    en_description,
    group_id
) VALUES
(  -- metric_id = 1
    'Метрика1',
    'Metric1',
    'Описание метрики',
    'Metric description',
    1
),
(  -- metric_id = 2
    'Метрика2',
    'Metric2',
    'Описание метрики2',
    'Metric2 description',
    2
),
(  -- metric_id = 3
    'Еще одна метрика',
    'One more metric',
    'Описание метрики3',
    'Metric3 description',
    1
)
;
