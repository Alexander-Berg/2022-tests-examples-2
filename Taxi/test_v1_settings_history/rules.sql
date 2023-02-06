INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, deleted, previous_version_id)
  VALUES
    (0, 'zero', 'return 0;', 'backend_only', '200ok', 00, '', '2010-03-04 06:00:00', true, null),
    (1, 'one', 'return 1;', 'backend_only', '200ok', 11, '', '2010-04-04 06:00:00', false, 0),
    (2, 'two', 'return 2;', 'backend_only', '200ok', 22, '', '2011-04-04 06:00:00', false, 1),
    (3, 'three', 'return 3;', 'both_side', '200ok', 33, '', '2012-04-04 06:00:00', false, 2),
    (4, 'four', 'return 4;', 'both_side', '200ok', 44, '', '2012-04-04 06:00:00', false, 3),
    (5, 'five', 'return 5;', 'both_side', '200ok', 55, '', '2012-04-04 06:00:00', false, 4)
;
