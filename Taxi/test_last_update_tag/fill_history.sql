INSERT INTO clients_schema.files (
    updated,
    mds_id,
    name,
    version,
    file_tag
) VALUES
    (CURRENT_TIMESTAMP,                      '1', 'name1', 1, 'normal_filled_tag'),
    (CURRENT_TIMESTAMP - interval '5 hours', '2', 'name2', 1, 'warn_filled_tag'),
    (CURRENT_TIMESTAMP - interval '7 hours', '3', 'name3', 1, 'crit_filled_tag');
