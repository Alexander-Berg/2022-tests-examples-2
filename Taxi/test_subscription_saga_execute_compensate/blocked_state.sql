INSERT INTO state.saga_steps(saga_id, name, execution_status, compensation_status)
VALUES ('1', 'driver_fix_stop_step', 'ok', NULL),
       ('1', 'driver_fix_start_step', 'ok', 'ok'),
       ('1', 'driver_fix_prepare_step', 'ok', Null),
       ('1', 'mode_change_step', 'blocked', 'ok'),
       ('2', 'driver_fix_stop_step', 'blocked', NULL),
       ('2', 'driver_fix_start_step', 'ok', NULL),
       ('2', 'driver_fix_prepare_step', 'ok', Null),
       ('2', 'mode_change_step', 'ok', NULL);
