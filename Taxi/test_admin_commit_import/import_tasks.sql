INSERT INTO personal_goals.import_tasks (
    import_task_id,
    yt_table_path,
    rows_count,
    last_row_index,
    failed_count,
    failed_details,
    status
) VALUES (
    '88db6b2edc064a3caf6d192846860227', '//path/to/table/1', 10, 5, 0, NULL, 'completed'
), (
    '88db6b2edc064a3caf6d192846860288', '//path/to/table/1', 10, 5, 2, '{"cause-a": [], "cause-b": ["x", "y"]}', 'completed'
), (
    'df79575218014715ba078fe25b73c016', '//path/to/table/3', 20, 2, 0, NULL, 'in_progress'
), (
    'fdedcdd557fe43c4bc00a394f23ac7e7', '//path/to/table/1', 10, NULL, 0, NULL, 'pending'
);
