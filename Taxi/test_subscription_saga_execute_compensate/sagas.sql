INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        prev_mode, prev_mode_timepoint, prev_mode_settings,
                        external_ref, accept_language, compensation_policy, source)
VALUES ('1', '2020-04-04 14:00:00+01', 'parkid1', 'uuid1', 'udi1', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"key": "nextvalue"}', 'prev_work_mode', '2020-05-16', '{"key": "prevvalue"}',
        'some_unique_key', 'ru', 'allow', 'manual_mode_change'),
       ('2', '2020-04-04 14:00:00+01', 'parkid2', 'uuid2', 'udi2', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"key": "nextvalue"}', 'prev_work_mode', '2020-05-16', '{"key": "prevvalue"}',
        'some_unique_key', 'ru', 'forbid', 'manual_mode_change');
