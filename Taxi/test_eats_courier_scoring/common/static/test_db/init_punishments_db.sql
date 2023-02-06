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
    (1, 'blocking', '{}', TRUE, now() - INTERVAL '2 DAY', 'long_block', 'region'),
    (1, 'blocking', '{}', TRUE, now() - INTERVAL '2 DAY', 'long_block', 'region'),
    (2, 'communication', '{}', TRUE, now() - INTERVAL '2 DAY', 'long_block', 'region'),
    (3, 'blocking', '{}', TRUE, now() - INTERVAL '3 DAY', 'long_block', 'region'),
    (4, 'blocking', '{}', TRUE, now() - INTERVAL '3 DAY', 'temp_block', 'region'),
    (5, 'blocking', '{}', TRUE, now() - INTERVAL '4 DAY', 'temp_block', 'region_2'),
    (6, 'blocking', '{}', TRUE, now() - INTERVAL '4 DAY', 'long_block', 'region_2'),
    (7, 'blocking', '{"blocking_days": 3}', TRUE, now() - INTERVAL '5 DAY', 'temp_block', 'region_3'),
    (8, 'blocking', '{"blocking_days": 10}', TRUE, now() - INTERVAL '5 DAY', 'temp_block', 'region_3');
