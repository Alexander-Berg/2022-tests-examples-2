INSERT INTO price_modifications.rules_drafts
    (rule_id, name, ast, source_code, policy, author, status, errors, updated, pmv_task_id, evaluate_on_prestable, prestable_evaluation_begin_time)
  VALUES
(1, 'one', '', 'return (2.2 / *ride.price) * ride.price;', 'backend_only', '200ok draft', 'failure', 'error message', '2014-06-04 06:00:00', 2, true, '2020-05-03 19:10:25+03')
;
