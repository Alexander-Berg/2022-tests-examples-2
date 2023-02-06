/* experiments */
INSERT INTO clients_schema.experiments (id,
                                        name,
                                        date_from, date_to,
                                        rev,
                                        description, enabled)
    VALUES (1,
            'trusted_files',
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            nextval('clients_schema.clients_rev'),
            'description', TRUE);

/* files */
INSERT INTO clients_schema.files (name, version, updated, mds_id, is_trusted)
  VALUES ('trusted_file', 1, CURRENT_TIMESTAMP, 'trusted_ec2f695e09044105bce60bdffd6a36ce', TRUE); -- 1
INSERT INTO clients_schema.files (name, version, updated, mds_id, is_trusted)
  VALUES ('non_trusted_file', 2, CURRENT_TIMESTAMP, 'non_trusted_c22efcd0226f40fa868a0143f344a3ef', FALSE); -- 2

/* link to experiments */
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, 'trusted_ec2f695e09044105bce60bdffd6a36ce');
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, 'non_trusted_c22efcd0226f40fa868a0143f344a3ef');
