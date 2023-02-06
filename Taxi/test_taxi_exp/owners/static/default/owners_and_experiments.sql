INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema)
        VALUES
            (1, ('superapp' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (2, ('map_view' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (3, ('exp_without_owners' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (4, ('exp_with_dismissed_owner' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (5, ('exprired_exp' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-01T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
;

INSERT INTO clients_schema.owners
    (experiment_id, owner_login)
        VALUES
            (1, 'first-login'),
            (1, 'another_login'),
            (2, 'another_login'),
            (4, 'dismissed-login'),
            (5, 'first-login')
;

select setval('clients_schema.experiments_id_seq', 6);
