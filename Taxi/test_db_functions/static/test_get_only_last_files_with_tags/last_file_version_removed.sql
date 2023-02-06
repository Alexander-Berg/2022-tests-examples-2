/*experiments */
INSERT INTO clients_schema.experiments (id, name, date_from, date_to, rev)
    VALUES (1, 'valid_experiment_name', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'));

/* file with tags and last is removed */
INSERT INTO clients_schema.files (name, version, updated, mds_id, file_tag, removed)
    VALUES
         ('f11', 1, CURRENT_TIMESTAMP, '1aaabbb', 'yandex', FALSE)
        ,('f11', 2, CURRENT_TIMESTAMP, '2cccccc', 'yandex', FALSE)
        ,('f11', 3, CURRENT_TIMESTAMP, '3dddddd', 'yandex', TRUE)
;
INSERT INTO clients_schema.experiments_tags (experiment_id, file_tag)
    VALUES (1, 'yandex')
;
