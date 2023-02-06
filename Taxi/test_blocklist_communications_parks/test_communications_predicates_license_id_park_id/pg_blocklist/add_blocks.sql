
INSERT INTO blocklist.blocks
    (id, predicate_id, revision, status, mechanics, reason)
VALUES
   ('10000000-0000-0000-0000-000000000000', '44444444-4444-4444-4444-444444444444', 1, 'active', 'mechanics_1', '{"key" : "reason_1"}' ),
   ('20000000-0000-0000-0000-000000000000', '44444444-4444-4444-4444-444444444444', 2, 'active', 'mechanics_1', '{"key" : "reason_1"}' );

INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'park_id', 'park-1'),
    ('10000000-0000-0000-0000-000000000000', 'license_id', 'license_1'),
    ('20000000-0000-0000-0000-000000000000', 'park_id', 'park-3'),
    ('20000000-0000-0000-0000-000000000000', 'license_id', 'license_3');
