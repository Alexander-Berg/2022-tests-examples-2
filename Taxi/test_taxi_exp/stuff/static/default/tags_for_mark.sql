INSERT INTO clients_schema.files (name, file_tag, mds_id, version, updated, is_trusted)
    VALUES
        ('fake_name_another_tag', 'another_tag', 'aaaaaaaa', 1, CURRENT_TIMESTAMP, TRUE),
        ('fake_name_another_tag', 'another_tag', 'bbbbbbbb', 2, CURRENT_TIMESTAMP, TRUE),
        ('fake_name_another_tag', 'another_tag', 'cccccccc', 3, CURRENT_TIMESTAMP, TRUE),
        ('fake_name_early_screening_non_processed_tag', 'early_screening_non_processed_tag', 'dddddddd', 1, CURRENT_TIMESTAMP, TRUE),
        ('fake_name_non_processed_tag', 'non_processed_tag', 'eeeeeeee', 1, CURRENT_TIMESTAMP, TRUE),
        ('fake_name_non_processed_tag', 'non_processed_tag', 'ffffffff', 2, CURRENT_TIMESTAMP, TRUE)
;
