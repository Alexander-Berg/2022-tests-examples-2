insert into db.script_tasks(id, script_body, var_constraints, task_state)
values
(1, '', '{}', 'InProgress'),
(2, '', '{}', 'Finished'),
(3, '', '{}', 'Finished');

insert into db.checks(id, script_id, check_type, message, task_state, check_body)
values
(1, 1, 'CheckNaN', '', 'InProgress', 'a'),
(2, 2, 'CheckNaN', '', 'InProgress', 'a'),
(3, 2, 'CheckNaN', '', 'Finished', 'b'),
(4, 3, 'CheckNaN', '', 'Finished', 'a')
;
