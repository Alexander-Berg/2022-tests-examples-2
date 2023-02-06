INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint,
                        external_ref, accept_language, change_reason, source)
VALUES ('1', '2020-05-16', 'parkid1', 'uuid1', 'udi1', 'orders',
        '2020-04-04 14:00:00+01',
        'some_unique_key', 'ru', 'low_taximeter_version', 'subscription_sync'),
       ('2', '2020-05-16', 'parkid2', 'uuid2', 'udi2', 'custom_orders',
        '2020-04-04 14:00:00+01',
        'some_unique_key', 'ru', 'driver_fix_expired', 'subscription_sync'),
       ('3', '2020-05-16', 'parkid3', 'uuid3', 'bannedparkid', 'orders',
        '2020-04-04 14:00:00+01',
        'some_unique_key', 'ru', 'banned_by_park', 'subscription_sync');
