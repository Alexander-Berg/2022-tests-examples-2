INSERT INTO clients_schema.files
    (mds_id, updated, file_tag, name, version)
    VALUES
        ('12345', CURRENT_TIMESTAMP, NULL, 'f1', 1),
        ('12346', CURRENT_TIMESTAMP, 'test_tag', 'f2', 1)
;
