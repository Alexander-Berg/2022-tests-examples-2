
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'bonus-10',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 10;'
),
(
    1,
    'bonus-20',
    0,
    '2019-02-03T01:00:00+00',
    'calculate',
    'return 20;'
),
(
    2,
    'bonus-30',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 30;'
),
(
    3,
    'bonus-40',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 40;'
),
(
    4,
    'bonus-50',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 50;'
),
(
    5,
    'bonus-for-driver-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 60;'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'bonus-10',
    'calculate',
    0
),
(
    1,
    '2019-02-03T00:00:00+00',
    'bonus-20',
    'calculate',
    1
),
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-30',
    'calculate',
    2
),
(
    3,
    '2019-02-03T00:00:00+00',
    'bonus-40',
    'calculate',
    3
),
(
    4,
    '2019-02-03T00:00:00+00',
    'bonus-50',
    'calculate',
    4
),
(
    5,
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'calculate',
    5
);
