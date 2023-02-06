INSERT INTO clients_schema.files (name, namespace, mds_id, version, updated)
    VALUES
        ('another', 'common', 'zzzzzzzz', 1, CURRENT_TIMESTAMP),
        ('another', 'common', 'yyyyyyyy', 2, CURRENT_TIMESTAMP),
        ('another', 'common', 'xxxxxxxx', 3, CURRENT_TIMESTAMP),
        ('early_screening_non_processed', NULL, 'tttttttt', 1, CURRENT_TIMESTAMP),
        ('non_processed', 'taxi', 'rrrrrrrr', 1, CURRENT_TIMESTAMP),
        ('non_processed', 'taxi', 'wwwwwwww', 2, CURRENT_TIMESTAMP)
;
