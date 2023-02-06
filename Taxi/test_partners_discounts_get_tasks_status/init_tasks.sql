INSERT INTO eats_discounts.tasks(task_id, status, message, modified_at, created_at, task_result)
VALUES ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa0', 'planned', NULL, '2021-01-01 00:00:00.000+00', '2021-01-01 00:00:00.000+00', NULL),
       ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'planned', NULL, '2021-01-02 00:00:00.000+00', '2021-01-01 00:00:00.000+00', NULL),
       ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'started', NULL, '2021-01-02 00:00:00.000+00', '2021-01-01 00:00:00.000+00', NULL),
       ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'failed', 'error', '2021-01-02 00:00:00.000+00', '2021-01-01 00:00:00.000+00', NULL),
       ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'failed', 'parse_error', '2021-01-02 00:00:00.000+00', '2021-01-01 00:00:00.000+00', NULL),
       ( 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'finished', NULL, '2021-01-02 00:00:00.000+00', '2021-01-01 00:00:00.000+00',
        '{"create_discounts":{"inserted_discount_ids":["1", "2", "3"],"affected_discount_ids":["4", "5", "6"]}}'::JSONB);
