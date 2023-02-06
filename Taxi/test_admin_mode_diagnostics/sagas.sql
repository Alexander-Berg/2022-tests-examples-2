INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        external_ref, accept_language, source)
VALUES ('1', '2019-05-01T05:00:00+00:00', 'park0', 'uuid0', 'udid0',
        'orders', '2019-05-01T05:00:00+00:00', '{"key":"next_value"}',
        'some_unique_key', 'ru', 'manual_mode_change');

INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        external_ref, accept_language, compensation_policy,
                        prev_mode, prev_mode_timepoint, prev_mode_settings, source)
VALUES ('2', '2019-05-01T05:00:00+00:00', 'park1', 'uuid1', 'udid1',
        'orders', '2019-05-01T05:00:00+00:00', '{"key":"next_value"}',
        'some_unique_key', 'ru', 'allow', 'driver_fix', '2019-05-01T04:00:00+00:00', '{"key":"prev_value"}','manual_mode_change');
