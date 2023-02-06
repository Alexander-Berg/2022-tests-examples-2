INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android');
INSERT INTO clients_schema.applications (name) VALUES ('ios');


-- experiment with false financial
INSERT INTO clients_schema.experiments (id, name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate,
                                        description,
                                        schema,
                                        is_technical, financial)
    VALUES
        (2, 'experiment_false_financial', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            TRUE,
            FALSE,
            nextval('clients_schema.clients_rev'),
            '{}',
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "not_null", "init": {"arg_name": "phone_id"}}'::jsonb,
            'Experiment with false financial',
            'additionalProperties: true',
            NULL,
            FALSE)
        ;
INSERT INTO clients_schema.experiments_applications (experiment_id,
                                                     application_id,
                                                     version_from,
                                                     version_to)
    VALUES
        (2, 1, '1.1', '100.100');
