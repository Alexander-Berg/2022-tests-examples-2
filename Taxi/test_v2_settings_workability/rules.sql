INSERT INTO price_modifications.rules
(name, source_code, policy, author, approvals_id, ast, updated, extra_return)
VALUES
('one', 'return 1;', 'backend_only', '200ok', 11, '', '2010-04-04 06:00:00', ARRAY['qqq']),
('two', 'return 2;', 'backend_only', '200ok', 22, '', '2011-04-04 06:00:00', ARRAY['qqq']),
('three', 'return 3;', 'both_side', '200ok', 33, '', '2012-04-04 06:00:00', ARRAY['ddd']),
('four', 'return 4;', 'backend_only', '200ok', 44, '', '2013-04-04 06:00:00', ARRAY['qqq']),
('five', 'return 5;', 'taximeter_only', '200ok', 55, '', '2014-04-04 06:00:00', ARRAY['zzz'])
;

INSERT INTO price_modifications.rules_drafts
(name, source_code, policy, author, status, errors, ast, updated, pmv_task_id)
VALUES
('a_draft', 'return 1.1;', 'backend_only', '200ok draft', 'running', NULL, '', '2014-05-04 06:00:00', 1),
('one', 'return 2.2;', 'backend_only', '200ok draft', 'failure', 'error message', '', '2014-06-04 06:00:00', 2), /* not "one_draft" for test with same names */
('two_draft', 'return 3.3;', 'backend_only', '200ok draft', 'running', 'error message', '', '2014-07-04 06:00:00', NULL),
('three_draft', 'return 4.4;', 'backend_only', '200ok draft', 'failure', 'error message', '', '2014-08-04 06:00:00', 4),
('four_draft', 'return 5.5;', 'both_side', '200ok draft', 'failure', 'error message', '', '2014-09-04 06:00:00', 5),
('five_draft', 'return 6.6;', 'taximeter_only', '200ok draft', 'failure', 'error message', '', '2014-10-04 06:00:00', 6)
;


