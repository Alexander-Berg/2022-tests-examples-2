INSERT INTO taxi_db_postgres_atlas_backend.solomon_metric_delivery_settings (
    metric_id,
    source_id,
    duration,
    grid
) VALUES
    (  -- delivery_id = 1
        1,
        3,
        300,  -- 5m
        60  -- 1m
    ),
    (  -- delivery_id = 2
        1,
        3,
        0,  -- 0s
        300  -- 5m
    )
;

INSERT INTO taxi_db_postgres_atlas_backend.solomon_metric_dimension (
    delivery_id, source_id, dimension_id
) VALUES
    (1, 3, 1),
    (1, 3, 5),
    (2, 3, 5)
;
