INSERT INTO clients_schema.experiments
    (name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed)
        VALUES
            (
                'check_map_style',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE);
