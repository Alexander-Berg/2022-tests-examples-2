INSERT INTO blocklist.blocks
    (id, predicate_id, revision, status, mechanics, reason)
VALUES
    ('10000000-0000-0000-0000-000000000000', '22222222-2222-2222-2222-222222222222', 1, 'active', 'mechanics_1', '{"key" : "reason_1"}' ),
    ('20000000-0000-0000-0000-000000000000', '22222222-2222-2222-2222-222222222222', 2, 'active', 'mechanics_1', '{"key" : "reason_1"}' );
INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'park_id', 'park_1'),
    ('10000000-0000-0000-0000-000000000000', 'car_number', 'САR_1'),

    ('20000000-0000-0000-0000-000000000000', 'park_id', 'park_2'),
    ('20000000-0000-0000-0000-000000000000', 'car_number', 'САR_2');
