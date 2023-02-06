INSERT INTO personal_goals.import_tasks (
    import_task_id,
    yt_table_path,
    rows_count,
    last_row_index,
    failed_count,
    status
) VALUES (
    '88db6b2edc064a3caf6d192846860288', '//path/to/table/1', 10, 5, 2, 'completed'
), (
    'df79575218014715ba078fe25b73c016', '//path/to/table/3', 20, 2, 0, 'in_progress'
), (
    'fdedcdd557fe43c4bc00a394f23ac7e7', '//path/to/table/1', 10, NULL, 0, 'pending'
);
