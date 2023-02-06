INSERT INTO surge.calculated
    (created, depot_id, pipeline, load_level)
VALUES
    ('2021-04-14T20:25:00.1234+03:00'::timestamptz, 'test_depot_1', 'test_pipeline_1', 1.1),
    ('2021-04-14T19:30:00.0001+03:00'::timestamptz, 'test_depot_1', 'test_pipeline_2', 1.2),
    ('2021-04-14T20:29:59.9999+03:00'::timestamptz, 'test_depot_2', 'test_pipeline_3', 1.3),
    ('2021-04-14T19:25:00.1234+03:00'::timestamptz, 'test_depot_1', 'test_pipeline_1', 1.4),
    ('2021-04-14T19:20:00.1234+03:00'::timestamptz, 'test_depot_1', 'test_pipeline_2', 1.5),
    ('2021-04-14T19:29:59.9999+03:00'::timestamptz, 'test_depot_2', 'test_pipeline_3', 1.6);
