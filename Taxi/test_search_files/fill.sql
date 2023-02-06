/*experiments */
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev) VALUES (1, 'n1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev) VALUES (2, 'n2', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev) VALUES (3, 'n3', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));

/* file with history and parent in experiment*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 1, CURRENT_TIMESTAMP, '1aaabbb'); -- 1
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 2, CURRENT_TIMESTAMP, '2cccccc'); -- 2
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 3, CURRENT_TIMESTAMP, '3dddddd'); -- 3
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, '1aaabbb');

/* file with history and child in experiment*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f21',
                                                                          1,
                                                                          CURRENT_TIMESTAMP,
                                                                          '231b3a60e38b47d0ab1e4fb42e4a4de1'); --4
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f21', 2, CURRENT_TIMESTAMP, '2a4de1'); -- 5
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f21', 3, CURRENT_TIMESTAMP, '3a4de1'); -- 6
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (3, '2a4de1');

/* file with history and nothing in experiment*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31',
                                                                          1,
                                                                          CURRENT_TIMESTAMP,
                                                                          '74807b81b2a9474a931b8eb968e0f838'); -- 7
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31', 2, CURRENT_TIMESTAMP, '2a931b8e'); -- 8
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31', 3, CURRENT_TIMESTAMP, '3a931b8e'); -- 9

/* file without history and in experiemnt*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f4', 1, CURRENT_TIMESTAMP, '4eeeeee'); -- 10
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (2, '4eeeeee');


/* file without history and not in experiemnt*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f5', 1, CURRENT_TIMESTAMP, '5ffffff'); -- 11

/* file with existing name */
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('existing_name',
                                                                          1,
                                                                          CURRENT_TIMESTAMP,
                                                                          'fd8de38e934c4c5e85e101b134602ac9'); -- 12

/* file with experiment_name */
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name) VALUES ('with_experiment_name',
                                                                                           1,
                                                                                           CURRENT_TIMESTAMP,
                                                                                           'b0070d7d47e04af8abcd83f154421741',
                                                                                           'experiment_by_user'); -- 13
