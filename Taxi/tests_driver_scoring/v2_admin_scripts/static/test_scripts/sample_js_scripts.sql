/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    10,
    'bonus-1',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 1'
),
(
    11,
    'bonus-1',
    1,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 1'
),
(
    12,
    'bonus-1',
    2,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 1'
),
(
    13,
    'bonus-1',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return 1'
),
(
    14,
    'bonus-2',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return 1'
);

INSERT INTO scripts.active_scripts
(bonus_name, type, script_id)
VALUES
(
    'bonus-1',
    'calculate',
    11
),
(
    'bonus-1',
    'filter',
    13
),
(
    'bonus-2',
    'filter',
    14
);
