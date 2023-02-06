INSERT INTO state.sagas(started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        prev_mode, prev_mode_timepoint, prev_mode_settings,
                        external_ref, accept_language, source)
VALUES ('2020-05-16', 'dbid0', 'uuid0', 'some_unique_id', 'orders',
        '2020-04-04 14:00:00+01', Null, 'driver_fix', '2020-05-16', '{"key":"prev_value"}',
        'some_unique_key', 'ru', 'manual_mode_change'),
       ('2020-05-16', 'dbid3', 'uuid3', 'some_unique_id', 'doctor_fix',
        '2020-04-04 14:00:00+01', '{"key":"next_value"}', 'driver_fix', '2020-05-16',
        '{"key":"prev_value"}',
        'some_unique_key', 'ru', 'manual_mode_change');
