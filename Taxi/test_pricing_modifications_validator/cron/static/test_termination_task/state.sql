insert into db.script_tasks(id, script_body, var_constraints, task_state, creation_time, last_update)
values
(1, '', '{}', 'InProgress', CURRENT_TIMESTAMP - INTERVAL '45' MINUTE, CURRENT_TIMESTAMP ),
(2, '', '{}', 'InProgress', CURRENT_TIMESTAMP - INTERVAL '25' MINUTE, CURRENT_TIMESTAMP ),
(3, '', '{}', 'InProgress', CURRENT_TIMESTAMP - INTERVAL '25' MINUTE, CURRENT_TIMESTAMP  - INTERVAL '20' MINUTE),
(4, '', '{}', 'InProgress', CURRENT_TIMESTAMP - INTERVAL '25' MINUTE, CURRENT_TIMESTAMP  - INTERVAL '10' MINUTE),
(5, '', '{}', 'Finished', CURRENT_TIMESTAMP - INTERVAL '45' MINUTE, CURRENT_TIMESTAMP )
;

insert into db.checks(id, script_id, check_type, message, comment)
values
(1, 1, 'CheckNaN', '', ''),
(2, 2, 'CheckNaN', '', ''),
(3, 3, 'CheckNaN', '', ''),
(4, 4, 'CheckNaN', '', ''),
(5, 5, 'CheckNaN', '', '')
;

