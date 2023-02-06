insert into db.script_tasks(id, script_body, var_constraints, task_state)
values
(1, '', '{}', 'New'),
(2, '', '{}', 'New'),
(3, '', '{}', 'New'),
(4, '', '{}', 'Terminated');

update db.script_tasks set creation_time = creation_time - interval '20 days'
where id = 1;

update db.script_tasks set last_update = last_update - interval '20 days'
where id = 3;
