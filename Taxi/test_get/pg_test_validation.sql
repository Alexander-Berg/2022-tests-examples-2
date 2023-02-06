insert INTO db.script_tasks(id, script_body, var_constraints, task_state)
VALUES
(1, 'R(1)', '{}', 'New'),
(2, 'R(B(1,/,0))', '{}', 'Finished'),
(3, 'R(B(1,/,B(B(ride,.,F(price)),.,F(distance))))', '{}', 'New')
;

INSERT INTO db.checks(script_id, check_body, check_type, message, task_state) VALUES
(1, 'check body', 'CheckNaN', '', 'InProgress'),
(2, 'check body', 'CheckNaN', 'Detected division by zero in variable 0', 'Finished'),
(3, 'check body', 'CheckNaN', 'Detected division by zero in variable ride.price.distance', 'Finished')
;

