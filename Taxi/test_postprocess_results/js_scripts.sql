
/* V1 */
INSERT INTO scripts.js_scripts
(bonus_name, revision, updated, type, content)
VALUES
(
    'bonus-for-driver-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 10;'
),
(
    'bonus-for-driver-tags',
    1,
    '2019-02-03T01:00:00+00',
    'calculate',
    'trace.text = "driver-tags"; return 20;'
),
(
    'penalty-for-approximate-position',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 30;'
),
(
    'bonus-for-class',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'trace.text = "bonus class"; return 40;'
),
(
    'bonus-for-surge',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 50;'
),
(
    'dynamic-bonus-for-reposition',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 0;'
),
(
    'dynamic-bonus-for-reposition',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return (order_context.search_from_request.order_id != "filter");'
),
(
    'penalty-for-verybusy',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 90;'
),
(
    'bonus-for-surges-ratio',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'throw "Error";'
),
(
    'ml-dispatch-bonus',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'while (true); return 80;'
),
(
    'bonus-for-user-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'if (order_context.user_tags && order_context.user_tags.includes(`some_user_tag_2`)) return 100; return 0;'
);

INSERT INTO scripts.active_scripts
(updated, bonus_name, type, script_id)
VALUES
(
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'calculate',
    1
),
(
    '2019-02-03T00:00:00+00',
    'penalty-for-approximate-position',
    'calculate',
    2
),
(
    '2019-02-03T00:00:00+00',
    'bonus-for-class',
    'calculate',
    3
),
(
    '2019-02-03T00:00:00+00',
    'bonus-for-surge',
    'calculate',
    4
),
(
    '2019-02-03T00:00:00+00',
    'dynamic-bonus-for-reposition',
    'calculate',
    5
),
(
    '2019-02-03T00:00:00+00',
    'dynamic-bonus-for-reposition',
    'filter',
    6
),
(
    '2019-02-03T00:00:00+00',
    'penalty-for-verybusy',
    'calculate',
    7
),
(
    '2019-02-03T00:00:00+00',
    'bonus-for-surges-ratio',
    'calculate',
    8
),
(
    '2019-02-03T00:00:00+00',
    'ml-dispatch-bonus',
    'calculate',
    9
),
(
    '2019-02-03T00:00:00+00',
    'bonus-for-user-tags',
    'calculate',
    10
);
