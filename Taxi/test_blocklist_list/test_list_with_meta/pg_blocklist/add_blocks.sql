INSERT INTO blocklist.blocks
    (id, predicate_id, revision)
VALUES
    ('10000000-0000-0000-0000-000000000000', '11111111-1111-1111-1111-111111111111', 1);

INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'park_id', 'park_1');

INSERT INTO blocklist.meta
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'meta_key', 'meta_val');
