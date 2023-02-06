INSERT INTO weariness.working_ranges
    (park_driver_profile_id, range_begin, range_end, updated_at, revision)
VALUES
    ('parkid_driverid', '2021-02-19T18:35:00+0300', '2021-02-19T18:45:00+0300', '2021-02-19T18:45:00+0300', 1),
    ('parkid_driverid_INCORRECT', '2021-02-19T18:51:00+0300', '2021-02-19T18:55:00+0300', '2021-02-19T18:53:00+0300', 2);

SELECT setval('weariness.working_ranges_revision', max_revision)
FROM (
    SELECT max(revision) max_revision
    FROM weariness.working_ranges)
subquery;
