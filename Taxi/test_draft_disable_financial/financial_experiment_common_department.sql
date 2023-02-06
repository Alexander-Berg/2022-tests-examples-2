INSERT INTO clients_schema.experiments
    (id,
     name,
     date_from, date_to,
     rev, clauses, predicate, description, enabled, schema, is_config, is_technical, default_value, department)
        VALUES
            (
                3,
                'common_department_experiment',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                TRUE,
                '{}'::jsonb,
                'common'
);
