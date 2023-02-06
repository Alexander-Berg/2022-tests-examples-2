INSERT INTO clients_schema.experiments
    (name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed, removed)
        VALUES
            (
                'removed_experiment',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                TRUE);
