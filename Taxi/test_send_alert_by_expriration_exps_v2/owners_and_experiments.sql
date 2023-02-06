INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, namespace)
        VALUES
            (1, ('exp_with_owner' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', NULL),
            (2, ('market_exp_with_owner' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', 'market'),
            (3, ('exp_owned_by_dismissed_person_a' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', NULL),
            (4, ('exp_owned_by_rotated_person_b' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', 'market'),
            (5, ('exp_owned_by_person_a_and_person_b' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', NULL),
            (6, ('exp_with_dismissed_owner_and_deleted_group' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', NULL),
            (7, ('exp_with_no_owners' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '', NULL)
;

INSERT INTO clients_schema.owners
    (experiment_id, owner_login, owner_group)
        VALUES
            (1, 'regular_employee', 10),
            (2, 'group_head', 10),
            (3, 'dismissed_person_a', 10),
            (4, 'rotated_person_b', 10),
            (5, 'dismissed_person_a', 10),
            (5, 'rotated_person_b', 10),
            (6, 'dismissed_person_c', 20)
;
