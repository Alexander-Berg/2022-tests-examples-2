INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema)
        VALUES
            ( 1, 'experiment_1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 2, 'experiment_2', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 3, 'experiment_3', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 4, 'experiment_4', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 5, 'experiment_5', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 6, 'experiment_6', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 7, 'experiment_7', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 8, 'experiment_8', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            ( 9, 'experiment_9', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, ''),
            (10, 'experiment_10', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '');
