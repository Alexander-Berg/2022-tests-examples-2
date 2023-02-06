INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android');
INSERT INTO clients_schema.applications (name) VALUES ('ios');


INSERT INTO clients_schema.experiments (name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate)
    VALUES
        ('test_experiment', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=1
            TRUE,
            FALSE,
            nextval('clients_schema.clients_rev'),
            '{}',
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb),
        ('experiment_with_empty_default', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=2
            TRUE,
            FALSE,
            nextval('clients_schema.clients_rev'),
            NULL,
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb),
        ('disabled_experiment', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=3
            FALSE,
            FALSE,
            nextval('clients_schema.clients_rev'),
            '{}',
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb),
        ('closed_experiment', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=4
            TRUE,
            TRUE,
            nextval('clients_schema.clients_rev'),
            '{}',
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb);

-- experiment with apps
INSERT INTO clients_schema.experiments (name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate)
    VALUES
        ('experiment_with_apps', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=5
            TRUE,
            FALSE,
            nextval('clients_schema.clients_rev'),
            '{}',
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb);
INSERT INTO clients_schema.experiments_applications (experiment_id,
                                                     application_id,
                                                     version_from,
                                                     version_to)
    VALUES
        (5, 1, '1.1', '100.100');

-- experiment with bad default value
INSERT INTO clients_schema.experiments (name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate)
    VALUES
        ('experiment_with_bad_default_value', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=6
         TRUE,
         FALSE,
         nextval('clients_schema.clients_rev'),
         'true'::jsonb,
         '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
         '{"type": "true"}'::jsonb);

-- experiment_with_existed_config
INSERT INTO clients_schema.experiments (name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate,
                                        is_config)
    VALUES
        ('experiment_with_existed_config', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=7
         TRUE,
         FALSE,
         nextval('clients_schema.clients_rev'),
         '{}'::jsonb,
         '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
         '{"type": "true"}'::jsonb,
         FALSE),
        ('experiment_with_existed_config', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,  -- id=8
         TRUE,
         FALSE,
         nextval('clients_schema.clients_rev'),
         '{}'::jsonb,
         '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
         '{"type": "true"}'::jsonb,
         TRUE)
    ;
