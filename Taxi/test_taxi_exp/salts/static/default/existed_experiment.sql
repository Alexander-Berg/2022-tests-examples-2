INSERT INTO clients_schema.experiments
    (name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed, is_config)
        VALUES
            (
                'existed_experiment',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                FALSE),
            (
                'existed_config',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                TRUE)
;
