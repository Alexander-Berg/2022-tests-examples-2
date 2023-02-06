/* experiments */
INSERT INTO clients_schema.experiments (id,
                                        name,
                                        date_from, date_to,
                                        rev,
                                        description, enabled)
    VALUES (1,
            'Новый эксперимент',
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            nextval('clients_schema.clients_rev'),
            'description', TRUE);

/* files */
INSERT INTO clients_schema.files (name, version, updated, mds_id)
  VALUES ('hard_linked_01', 1, CURRENT_TIMESTAMP, 'ec2f695e09044105bce60bdffd6a36ce'); -- 1
INSERT INTO clients_schema.files (name, version, updated, mds_id)
  VALUES ('hard_linked_02', 2, CURRENT_TIMESTAMP, 'c22efcd0226f40fa868a0143f344a3ef'); -- 2
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name)
  VALUES ('soft_linked', 3, CURRENT_TIMESTAMP,
          'f3a4a5dd034c4a9cada26b2b35f1f06e',
          'Новый эксперимент'); -- 3


/* link to experiments */
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, 'ec2f695e09044105bce60bdffd6a36ce');
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, 'c22efcd0226f40fa868a0143f344a3ef');
