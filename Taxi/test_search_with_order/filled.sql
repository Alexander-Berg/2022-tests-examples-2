INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, default_value, description, enabled, schema, created, last_manual_update)
        VALUES
            (
                1,
                'first_experiment',
                '2020-03-25 18:54:05',
                '2022-03-25 18:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                '2020-03-23 21:54:05',
                '2020-03-24 12:54:05'
            )
            ,(
                2,
                'second_experiment',
                '2020-03-25 20:54:05',
                '2022-03-25 21:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                '2020-03-23 11:54:05',
                '2020-03-24 22:54:05'
            )
            ,(
                3,
                'third_experiment',
                '2020-03-25 19:54:05',
                '2022-03-25 20:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                '2020-03-24 11:04:05',
                '2020-03-25 12:00:05'
            )
;

INSERT INTO clients_schema.owners
    (experiment_id, owner_login)
    VALUES
        (1, 'serg-novikov'),
        (2, 'luxenia'),
        (3, 'luxenia')
;

INSERT INTO clients_schema.watchers
    (experiment_id, watcher_login, last_revision)
    VALUES
        (1, 'luxenia', 0),
        (1, 'axolm', 0),
        (2, 'serg-novikov', 0),
        (3, 'axolm', 0)
;
