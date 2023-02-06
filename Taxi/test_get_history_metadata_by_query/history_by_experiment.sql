/* experiment */
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev)
    VALUES (1, 'n1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));

/* history by experiment */
INSERT INTO
  clients_schema.files_history (id, mds_id, name, action_type, updation_time, experiment_id)
    VALUES
        (nextval('clients_schema.files_history_id_seq'), '11111', 'user_ids.txt', 'create', CURRENT_TIMESTAMP, 1),
        (nextval('clients_schema.files_history_id_seq'), '11111', 'user_ids.txt', 'update', CURRENT_TIMESTAMP, 1),
        (nextval('clients_schema.files_history_id_seq'), '22222', 'user_ids.txt', 'create', CURRENT_TIMESTAMP, 1)
;

/* config */
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev, is_config)
    VALUES (2, 'n1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), TRUE);

/* history by config */
INSERT INTO
  clients_schema.files_history (id, mds_id, name, action_type, updation_time, experiment_id)
    VALUES
        (nextval('clients_schema.files_history_id_seq'), 'c11111', 'config_user_ids.txt', 'create', CURRENT_TIMESTAMP, 2),
        (nextval('clients_schema.files_history_id_seq'), 'c11111', 'config_user_ids.txt', 'update', CURRENT_TIMESTAMP, 2),
        (nextval('clients_schema.files_history_id_seq'), 'c22222', 'config_user_ids.txt', 'create', CURRENT_TIMESTAMP, 2)
;
