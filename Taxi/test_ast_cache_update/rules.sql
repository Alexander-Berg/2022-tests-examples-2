INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast, updated)
VALUES
  (10, 'surge', 'return ride.price;', 'both_side', '200ok', 1, '', '2018-05-04 06:00:00')
;

INSERT INTO price_modifications.rules_drafts
    (name, source_code, policy, author, status, errors, ast, updated, pmv_task_id) values
    ('surge', 'return ride.price;', 'both_side', '200ok draft', 'to_approve', NULL, '', '2014-05-04 06:00:00', 1);
