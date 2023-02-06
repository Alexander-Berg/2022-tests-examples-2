INSERT INTO clients_schema.experiments
    (
        id, name, date_from, date_to,
        rev, clauses, predicate, description,
        enabled, schema, closed, created, last_manual_update,
        department
    )
        VALUES
            (
                1,
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
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                'commando'
            )
;

INSERT INTO clients_schema.applications
    (id, name) VALUES (2, 'iphone');

INSERT INTO clients_schema.files
    (mds_id, name, version, updated)
        VALUES
            ('aaaaabbbb', 'first_file', 1, CURRENT_TIMESTAMP)
;

INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android');

-- Create links

INSERT INTO clients_schema.experiments_applications
    (experiment_id, application_id, version_from, version_to)
        VALUES
            (1, 1, '1.1.1', '10.1.1')
            ,(1, 2, '1.1.1', '10.1.1')
;

INSERT INTO clients_schema.experiments_consumers
    (experiment_id, consumer_id)
        VALUES
            (1, 1)
;

INSERT INTO clients_schema.experiments_files
    (experiment_id, file_id)
        VALUES
            (1, 'aaaaabbbb')
;
