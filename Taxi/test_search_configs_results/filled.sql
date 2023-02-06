INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, default_value, description, enabled, schema, created, last_manual_update, is_config)
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
                '2020-03-23 18:54:05',
                '2020-03-24 12:54:05',
                TRUE
            )
            ,(
                2,
                'second_experiment',
                '2020-03-25 18:54:05',
                '2022-03-25 18:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                '2020-03-23 11:54:05',
                '2020-03-24 22:54:05',
                TRUE
            )
            ,(
                3,
                'third_experiment',
                '2020-03-25 18:54:05',
                '2022-03-25 18:54:05',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                '{}'::jsonb,
                'DESCRIPTION',
                TRUE,
                'type: object\nadditionalProperties: false',
                '2020-03-24 11:04:05',
                '2020-03-25 12:00:05',
                TRUE
            )
;
