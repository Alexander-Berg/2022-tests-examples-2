INSERT INTO clients_schema.files (name, mds_id, version, removed, updated)
    VALUES
        ('existed_in_s3', 'aaaaaaaa', 1, TRUE, CURRENT_TIMESTAMP),
        ('existed_in_s3', 'bbbbbbbb', 2, TRUE, CURRENT_TIMESTAMP),
        ('existed_in_s3', 'cccccccc', 3, FALSE, CURRENT_TIMESTAMP),
        ('non_existed_in_s3', 'ddddddd', 1, TRUE, CURRENT_TIMESTAMP)
;
