/* experiments */
INSERT INTO clients_schema.experiments (id,
                                        name,
                                        date_from, date_to,
                                        rev,
                                        description, enabled
    ) VALUES (1, 'n1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), 'description', TRUE);
INSERT INTO clients_schema.experiments (id,
                                        name,
                                        date_from, date_to,
                                        rev,
                                        description, enabled
    ) VALUES (2, 'n2', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), 'description', TRUE);
INSERT INTO clients_schema.experiments (id,
                                        name,
                                        date_from, date_to,
                                        rev,
                                        description, enabled
    ) VALUES (3, 'n3', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), 'description', TRUE);

/* file */
INSERT INTO clients_schema.files (name,
                                  version,
                                  updated,
                                  mds_id
    ) VALUES ('f11', 1, CURRENT_TIMESTAMP, 'ec2f695e09044105bce60bdffd6a36ce'); -- 1

/* link to experiments */
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, 'ec2f695e09044105bce60bdffd6a36ce');
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (2, 'ec2f695e09044105bce60bdffd6a36ce');
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (3, 'ec2f695e09044105bce60bdffd6a36ce');
