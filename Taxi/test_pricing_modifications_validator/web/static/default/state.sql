insert into db.script_tasks(id, script_body, var_constraints, task_state)
values
(1, '', '{}', 'InProgress'),
(2, '', '{}', 'New'),
(3, '', '{}', 'Finished');

insert into db.checks(id, script_id, check_type, message, comment)
values
(1, 1, 'CheckNaN', '', ''),
(2, 2, 'CheckNaN', '', ''),
(3, 3, 'CheckNaN', '', '')
;

insert into db.eq_systems(id, check_id, body, comment, task_state)
values
(1, 1, '', '', 'New'),
(2, 1, '', '', 'InProgress'),
(3, 1, '', '', 'InProgress'),
(4, 1, '', '', 'Finished'),
(6, 1, '', '', 'Finished'),
(7, 1, '', '', 'Cancelled');
