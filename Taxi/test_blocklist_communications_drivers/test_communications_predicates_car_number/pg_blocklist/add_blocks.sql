INSERT INTO blocklist.blocks
    (id, predicate_id, revision, status, mechanics, reason)
VALUES
    ('10000000-0000-0000-0000-000000000000', '11111111-1111-1111-1111-111111111111', 1, 'active', 'mechanics_1', '{"key" : "reason_1"}' ),
    ('20000000-0000-0000-0000-000000000000', '11111111-1111-1111-1111-111111111111', 2, 'active', 'mechanics_1', '{"key" : "reason_1"}' );
INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'car_number', 'САR_2'),
    ('20000000-0000-0000-0000-000000000000', 'car_number', 'САR_1');
