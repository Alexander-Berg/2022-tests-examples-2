INSERT INTO price_modifications.rules_drafts
    (name, source_code, policy, author, status, pmv_task_id, approvals_id, ast, updated)
  VALUES
    ('without_pmv_task_id', 'return 1.0;', 'backend_only', '200ok', 'running', NULL, NULL, 'R(1.0)', '2020-01-01 00:00:00'),
    ('in_progress', 'return 1.0;', 'backend_only', '200ok', 'running', 1, NULL, 'R(1.0)', '2020-01-01 00:00:00'),
    ('status_ok', 'return 1.0;', 'backend_only', '200ok', 'running', 2, 22, 'R(1.0)', '2020-01-01 00:00:00'),
    ('status_warning', 'return 1.0;', 'backend_only', '200ok', 'running', 3, 33, 'R(1.0)', '2020-01-01 00:00:00'),
    ('status_error', 'return 1.0;', 'backend_only', '200ok', 'running', 4, 44, 'R(1.0)', '2020-01-01 00:00:00'),
    ('empty_results', 'return 1.0;', 'backend_only', '200ok', 'running', 5, 55, 'R(1.0)', '2020-01-01 00:00:00'),
    ('response500', 'return 1.0;', 'backend_only', '200ok', 'running', 6, NULL, 'R(1.0)', '2020-01-01 00:00:00'),
    ('response404', 'return 1.0;', 'backend_only', '200ok', 'running', 8, NULL, 'R(1.0)', '2020-01-01 00:00:00'),
    ('response512', 'return 1.0;', 'backend_only', '200ok', 'running', 7, NULL, 'R(1.0)', '2020-01-01 00:00:00')
;
