INSERT INTO limits.windows (limit_ref, type, size, value, threshold, label, start, ticket, last_notified_wid)
VALUES
    ('tumbling', 'tumbling', 604800, 10000, 100, 'Недельный', '2000-01-01T18:00:00.000000+00:00', null, null),
    ('sliding', 'sliding', 604800, 10000, 120, '7-дневный', null, null, null),
    ('test_comment', 'sliding', 60, 10, 120, 'label', null, 'TAXIBUDGETALERT-10', null),
    ('test_notified', 'sliding', 60, 10, 120, 'label', null, null, 18232),
    ('8811c56a-1f84-11eb-8086-5366a7d74448', 'sliding', 60, 10, 120, 'label', null, null, null),
    ('account_id', 'sliding', 60, 10, 120, 'label', null, null, null)
;
