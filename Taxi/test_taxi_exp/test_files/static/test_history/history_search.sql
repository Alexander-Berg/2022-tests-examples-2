INSERT INTO
  clients_schema.files_history (id, mds_id, name, action_type, updation_time)
    VALUES (nextval('clients_schema.files_history_id_seq'), '11111', 'user_ids.txt', 'create', CURRENT_TIMESTAMP);

INSERT INTO
  clients_schema.files_history (id, mds_id, name, action_type, updation_time)
    VALUES (nextval('clients_schema.files_history_id_seq'), '11111', 'user_ids.txt', 'update', CURRENT_TIMESTAMP);

INSERT INTO
  clients_schema.files_history (id, mds_id, name, action_type, updation_time)
    VALUES (nextval('clients_schema.files_history_id_seq'), '22222', 'user_ids.txt', 'create', CURRENT_TIMESTAMP);
