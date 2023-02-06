INSERT INTO state.saga_steps(saga_id, name, execution_status, compensation_status)
VALUES ('1', 'ui_profile_change_step', 'ok', NULL),
       ('1', 'mode_change_step', 'blocked', 'ok');
