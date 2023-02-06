INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema)
        VALUES
            (1, ('superapp' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (2, ('map_view' COLLATE "C.UTF-8"), '2019-01-05T12:00:00'::timestamp, '2019-01-11T12:00:00'::timestamp, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
;

UPDATE clients_schema.experiments
    SET rev = nextval('clients_schema.clients_rev')
    WHERE id = 1;

INSERT INTO clients_schema.experiments_history
    (rev, body, name, is_config)
        VALUES
            (1, '{}'::jsonb, 'superapp', FALSE),
            (2, '{}'::jsonb, 'map_view', FALSE),
            (3, '{}'::jsonb, 'superapp', FALSE)
;

INSERT INTO clients_schema.revision_history
    (experiment_id, rev, updated)
        VALUES
            (1, 1, '2019-01-05T12:00:00'::timestamp),
            (1, 3, '2019-01-06T12:00:00'::timestamp),
            (2, 2, '2019-01-06T12:00:00'::timestamp)
;

INSERT INTO clients_schema.watchers
    (experiment_id, watcher_login, last_revision)
        VALUES
            (1, 'first-login', 1),
            (1, 'another_login', 3),
            (2, 'another_login', 2)
;
