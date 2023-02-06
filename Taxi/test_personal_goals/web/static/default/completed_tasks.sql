-- we can have more than one 'completed' task but only one
-- in 'pending'/'in_progress' statuses
INSERT INTO personal_goals.import_tasks (
    import_task_id,
    yt_table_path,
    rows_count,
    last_row_index,
    failed_count,
    status
) VALUES (
    '88db6b2edc064a3caf6d192846860227', '//path/to/table/1', 10, 5, 3, 'completed'
), (
    'ebe100a3ed93457a894d04d561fac78c', '//path/to/table/2', 15, 7, 0, 'completed'
), (
    'df79575218014715ba078fe25b73c016', '//path/to/table/3', 20, 2, 1, 'in_progress'
), ( -- second task started for first table
    'fdedcdd557fe43c4bc00a394f23ac7e7', '//path/to/table/1', 10, NULL, 0, 'pending'
);
