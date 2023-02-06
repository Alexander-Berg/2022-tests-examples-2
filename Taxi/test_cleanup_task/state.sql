insert into db.script_tasks(id, script_body, var_constraints, task_state, last_update)
values
(1, '', '{}', 'Finished', CURRENT_TIMESTAMP - INTERVAL '6 DAYS'),
(2, '', '{}', 'Finished', CURRENT_TIMESTAMP - INTERVAL '6 DAYS'),
(3, '', '{}', 'Finished', CURRENT_TIMESTAMP - INTERVAL '8 DAYS'),
(4, '', '{}', 'InProgress', CURRENT_TIMESTAMP - INTERVAL '8 DAYS');

insert into db.checks(id, script_id, check_type, message, comment)
values
(1, 1, 'CheckNaN', '', ''),
(2, 2, 'CheckNaN', '', ''),
(3, 3, 'CheckNaN', '', ''),
(4, 4, 'CheckNaN', '', '')
;

