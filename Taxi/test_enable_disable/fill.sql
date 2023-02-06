INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android'), ('ios');

INSERT INTO clients_schema.experiments (id,
                                        name,
                                        rev,
                                        is_config,
                                        date_from, date_to,
                                        default_value,
                                        clauses,
                                        predicate,
                                        description,
                                        enabled,
                                        schema)
    VALUES
        (
            1,
            'n1-enabled',
            nextval('clients_schema.clients_rev'),
            FALSE,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            NULL,
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb,
            'DESCRIPTION',
            TRUE,
            'additionalProperties: true')
        ,(
            2,
            'n1-enabled',
            nextval('clients_schema.clients_rev'),
            TRUE,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            '{}'::jsonb,
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb,
            'DESCRIPTION',
            TRUE,
            'additionalProperties: true')
        ,(
            3,
            'n1-disabled',
            nextval('clients_schema.clients_rev'),
            FALSE,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            '{}'::jsonb,
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb,
            'DESCRIPTION',
            FALSE,
            'additionalProperties: true')
        ,(
            4,
            'n1-disabled',
            nextval('clients_schema.clients_rev'),
            TRUE,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            '{}'::jsonb,
            '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}}]'::jsonb,
            '{"type": "true"}'::jsonb,
            'DESCRIPTION',
            FALSE,
            'additionalProperties: true')
;
