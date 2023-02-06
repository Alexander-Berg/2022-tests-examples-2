INSERT INTO weariness.working_ranges
    (park_driver_profile_id, range_begin, range_end, updated_at, revision)
VALUES
    ('park1_driverSS1', '2021-02-19T15:35:00+0300', '2021-02-19T15:45:00+0300', '2021-02-19T15:45:00+0300', 1),
    ('park1_driverSS1', '2021-02-19T15:51:00+0300', '2021-02-19T15:53:00+0300', '2021-02-19T18:53:00+0300', 2),
    ('park1_driverSS1', '2021-02-19T17:01:00+0300', '2021-02-19T18:50:00+0300', '2021-02-19T18:54:00+0300', 3),
    ('dbid_uuid40',    '2021-02-18T18:30:00+0300', '2021-02-18T18:42:00+0300', '2021-02-18T18:42:00+0300', 4),
    ('dbid_uuid40',    '2021-02-19T14:45:00+0300', '2021-02-19T14:54:00+0300', '2021-02-19T14:54:00+0300', 5);

SELECT setval('weariness.working_ranges_revision', max_revision)
FROM (
    SELECT max(revision) max_revision
    FROM weariness.working_ranges)
subquery;
