INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        prev_mode, prev_mode_timepoint, prev_mode_settings,
                        external_ref, accept_language, source)
VALUES ('1', '2020-05-16', 'parkid1', 'uuid1', 'udi1', 'orders',
        '2020-04-04 14:00:00+03', Null, 'orders', '2020-05-16', Null,
        'some_unique_key', 'ru', 'manual_mode_change'),
       ('2', '2020-05-16', 'parkid2', 'uuid2', 'udi2', 'custom_orders',
        '2020-04-04 14:00:00+03', '{"key":"value"}', 'orders', '2020-05-16',
        Null,
        'some_unique_key', 'ru', 'manual_mode_change');
