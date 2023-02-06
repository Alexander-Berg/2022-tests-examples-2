INSERT INTO processing.events (scope, queue, item_id, event_id, updated, is_archivable)
VALUES
       ('abc', 'queue 2', '0001', 'event 1',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        false),
       ('vvv', 'queue 4', '0002', 'event 1',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        true),
        ('vvv', 'queue 4', '0002', 'event 2',
        '2020-01-28T15:55:01.4183+03:00'::timestamptz,
        true);
