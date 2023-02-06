INSERT INTO blocklist.predicates
    (id, value, kwarg_keys, indexible_kwargs, designation)
VALUES
    ('9b3294fe-ea19-471c-890e-1977a18f0a61', '{"type": "eq","value": "park_id"}', ARRAY['park_id'], ARRAY['park_id'], 'park_id');

INSERT INTO blocklist.blocks
    (id, predicate_id, revision, status, mechanics, reason)
VALUES
    ('10000000-0000-0000-0000-000000000000', '9b3294fe-ea19-471c-890e-1977a18f0a61', 1, 'active', 'mechanics_1', '{"key" : "reason_1"}' ),
    ('20000000-0000-0000-0000-000000000000', '9b3294fe-ea19-471c-890e-1977a18f0a61', 2, 'active', 'mechanics_1', '{"key" : "reason_1"}' ),
    ('30000000-0000-0000-0000-000000000000', '9b3294fe-ea19-471c-890e-1977a18f0a61', 3, 'active', 'mechanics_1', '{"key" : "reason_1"}' );

INSERT INTO blocklist.kwargs
    (block_id, key, value)
VALUES
    ('10000000-0000-0000-0000-000000000000', 'park_id', 'park-1'),
    ('20000000-0000-0000-0000-000000000000', 'park_id', 'park-2'),
    ('30000000-0000-0000-0000-000000000000', 'park_id', 'park-3');
