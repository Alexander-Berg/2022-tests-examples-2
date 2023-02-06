INSERT INTO eats_courier_scoring.punishments(
    courier_id,
    punishment_type,
    arguments,
    is_sent,
    created_at,
    punishment_name,
    region_name
)
VALUES
    (1, 'blocking', '{"blocking_days": 3}', TRUE, now() - INTERVAL '2 DAY', 'permanent_block', 'region'),
    (1, 'blocking', '{"blocking_days": 3}', TRUE, now() - INTERVAL '2 DAY', 'permanent_block', 'region'),
    (1, 'blocking', '{"blocking_days": 3}', TRUE, now() - INTERVAL '4 DAY', 'permanent_block', 'region'),
    (2, 'blocking', '{"blocking_days": 3}', FALSE, now() - INTERVAL '2 DAY', 'permanent_block', 'region'),
    (3, 'blocking', '{"blocking_days": "3"}', TRUE, now() - INTERVAL '4 DAY', 'permanent_block', 'region'),
    (4, 'blocking', '{"blocking_days": 3}', TRUE, now() - INTERVAL '2 DAY', 'permanent_block', 'region_2'),
    (5, 'blocking', '{}', TRUE, now() - INTERVAL '2 DAY', 'permanent_block', 'region'),
    (6, 'blocking', '{}', TRUE, now() - INTERVAL '4 DAY', 'permanent_block', 'region');
