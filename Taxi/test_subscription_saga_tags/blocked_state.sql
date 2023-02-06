INSERT INTO state.saga_steps(saga_id, name, execution_status, compensation_status)
VALUES ('1', 'tags_change_step', 'ok', NULL),
       ('1', 'mode_change_step', 'blocked', 'ok'),
       ('2', 'tags_change_step', 'ok', NULL),
       ('2', 'mode_change_step', 'blocked', 'ok')
