INSERT INTO clients_schema.experiments
    (name,
     date_from, date_to,
     rev, clauses, predicate, description, enabled, schema, is_config, is_technical, default_value, department)
        VALUES
            (
                'config_test_draft',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                TRUE,
                TRUE,
                '{}'::jsonb,
                'market'
);
