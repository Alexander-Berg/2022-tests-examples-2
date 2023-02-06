INSERT INTO state.saga_steps(saga_id, name, execution_status, compensation_status)
VALUES ('1', 'logistic_workshifts_start', 'ok', NULL),
       ('1', 'logistic_workshifts_stop', 'ok', NULL),
       ('1', 'mode_change_step', 'blocked', 'ok');
