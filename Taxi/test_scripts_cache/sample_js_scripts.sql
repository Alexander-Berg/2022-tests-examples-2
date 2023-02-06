
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'bonus-1',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return undefined;'
),
(
    1,
    'bonus-1',
    1,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return undefined;'
),
(
    2,
    'bonus-1',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return undefined;'
),
(
    3,
    'bonus-2',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return undefined;'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'bonus-1',
    'calculate',
    1
),
(
    1,
    '2019-02-03T00:00:00+00',
    'bonus-1',
    'filter',
    2
),
(
    3,
    '2019-02-03T00:00:00+00',
    'bonus-2',
    'calculate',
    3
);
