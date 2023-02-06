
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'bonus-for-driver-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 100;'
),
(
    1,
    'bonus-for-driver-tags',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return candidate_context.candidate_from_request.id === "dbid1_uuid1";'
),
(
    2,
    'bonus-for-class',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 200;'
);


INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'calculate',
    0
),
(
    1,
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'filter',
    1
),
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-class',
    'calculate',
    2
);
