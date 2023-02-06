INSERT INTO blocklist.blocks
    (id, predicate_id, revision, status, mechanics, reason)
VALUES
    ('10000000-0000-0000-0000-000000000000', '33333333-3333-3333-3333-333333333333', 1, 'active', 'mechanics_1', '{"key" : "reason_1"}' );
INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'license_id', 'license_1');
