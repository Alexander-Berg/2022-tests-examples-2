INSERT INTO state.saga_steps(saga_id, name, execution_status, compensation_status)
VALUES ('1', 'driver_fix_stop_step', 'failed', Null),
       ('1', 'driver_fix_start_step', 'ok', 'ok'),
       ('1', 'driver_fix_prepare_step', 'ok', 'ok'),
       ('1', 'mode_change_step', 'ok', 'ok');
