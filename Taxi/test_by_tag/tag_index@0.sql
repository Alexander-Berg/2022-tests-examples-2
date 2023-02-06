INSERT INTO bd_testsuite_01.tag_index
(
    tag,
    event_at,
    doc_id
)
VALUES
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-01 07:07:52.019582'::timestamp,
    10001
),
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-02 07:07:52.019582'::timestamp,
    20001
),
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-03 07:07:52.019582'::timestamp,
    30001
),
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-04 07:07:52.019582'::timestamp,
    40001
),
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-05 07:07:52.019582'::timestamp,
    50001
),
(
    'taxi/unique_driver_id/5c6527563fd6940450db7483',
    '2018-09-06 07:07:52.019582'::timestamp,
    60001
);


INSERT INTO bd_testsuite_02.tag_index
(
    tag,
    event_at,
    doc_id
)
VALUES
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-09 07:07:52.019582'::timestamp,
    50002
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-10 07:07:52.019582'::timestamp,
    20000
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-10 07:07:52.019582'::timestamp,
    60004
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-11 07:07:52.019582'::timestamp,
    60002
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-12 07:07:52.019582'::timestamp,
    70004
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-13 07:07:52.019582'::timestamp,
    70002
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-14 06:07:52.019582'::timestamp,
    -- does not exist
    9999999990004
),
(
    'taxi/unique_driver_id/5c615efb3fd6947b66fc2e79',
    '2018-09-14 07:07:52.019582'::timestamp,
    80004
);
