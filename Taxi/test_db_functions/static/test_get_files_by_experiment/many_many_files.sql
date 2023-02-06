/*experiments */
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev)
    VALUES (1, 'valid_experiment_name', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));

/* last file with history and parent hardlinked in experiment */
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 1, CURRENT_TIMESTAMP, '1aaabbb'); -- 1
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 2, CURRENT_TIMESTAMP, '2cccccc'); -- 2
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f11', 3, CURRENT_TIMESTAMP, '3dddddd'); -- 3
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, '3dddddd');

/* non last file with history in experiment*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31',
                                                                          1,
                                                                          CURRENT_TIMESTAMP,
                                                                          '74807b81b2a9474a931b8eb968e0f838'); -- 4
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31', 2, CURRENT_TIMESTAMP, '2a931b8e'); -- 5
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f31', 3, CURRENT_TIMESTAMP, '3a931b8e'); -- 6
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, '74807b81b2a9474a931b8eb968e0f838');

/* file without history and in experiemnt*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f4', 1, CURRENT_TIMESTAMP, '4eeeeee'); -- 7
INSERT INTO clients_schema.experiments_files (experiment_id, file_id) VALUES (1, '4eeeeee');

/* file with history and parent softlinked in experiment*/
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name)
    VALUES ('f11_in_exp', 1, CURRENT_TIMESTAMP, 'adee6a31f62b4d89', 'valid_experiment_name'); -- 8
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name)
    VALUES ('f11_in_exp', 2, CURRENT_TIMESTAMP, '89ec5a89b8f7b2f9', 'valid_experiment_name'); -- 9
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name)
    VALUES ('f11_in_exp', 3, CURRENT_TIMESTAMP, 'a677c9d22f664b87', 'valid_experiment_name'); -- 10

/* file without history softlinked in experiemnt*/
INSERT INTO clients_schema.files (name, version, updated, mds_id, experiment_name)
    VALUES ('f4_in_exp', 1, CURRENT_TIMESTAMP, '9452f5385ca54e4a', 'valid_experiment_name'); -- 11

/* file without history and not in experiemnt*/
INSERT INTO clients_schema.files (name, version, updated, mds_id) VALUES ('f5', 1, CURRENT_TIMESTAMP, '5ffffff'); -- 12
