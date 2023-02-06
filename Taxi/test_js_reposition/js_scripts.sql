
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
    'return 10;'
),
(
    1,
    'bonus-for-driver-tags',
    1,
    '2019-02-03T01:00:00+00',
    'calculate',
    'trace.text = "driver-tags"; return 20;'
),
(
    2,
    'penalty-for-approximate-position',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 30;'
),
(
    3,
    'bonus-for-class',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'trace.text = "bonus class"; return 40;'
),
(
    4,
    'bonus-for-surge',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 50;'
),
(
    5,
    'dynamic-bonus-for-reposition',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
        if (candidate_context.reposition_check_result) {
            var reposition_check_result = candidate_context.reposition_check_result;

            if (reposition_check_result.score && reposition_check_result.score_parameters) {
                var score = reposition_check_result.score;
                var score_parameters = reposition_check_result.score_parameters;

                var b = score_parameters.b;
                var c = score_parameters.c;
                var d = score_parameters.d;

                return b + (score ** c) * d;
            }
        }

        return 60;
    '
),
(
    6,
    'dynamic-bonus-for-reposition',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return true;'
),
(
    7,
    'penalty-for-verybusy',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 90;'
),
(
    8,
    'bonus-for-surges-ratio',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'throw "Error";'
),
(
    9,
    'ml-dispatch-bonus',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'while (true); return 80;'
),
(
    10,
    'bonus-for-user-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'if (order_context.user_tags && order_context.user_tags.includes(`some_user_tag_2`)) return 100; return 0;'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'calculate',
    1
),
(
    1,
    '2019-02-03T00:00:00+00',
    'penalty-for-approximate-position',
    'calculate',
    2
),
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-class',
    'calculate',
    3
),
(
    3,
    '2019-02-03T00:00:00+00',
    'bonus-for-surge',
    'calculate',
    4
),
(
    4,
    '2019-02-03T00:00:00+00',
    'dynamic-bonus-for-reposition',
    'calculate',
    5
),
(
    5,
    '2019-02-03T00:00:00+00',
    'dynamic-bonus-for-reposition',
    'filter',
    6
),
(
    6,
    '2019-02-03T00:00:00+00',
    'penalty-for-verybusy',
    'calculate',
    7
),
(
    7,
    '2019-02-03T00:00:00+00',
    'bonus-for-surges-ratio',
    'calculate',
    8
),
(
    8,
    '2019-02-03T00:00:00+00',
    'ml-dispatch-bonus',
    'calculate',
    9
),
(
    9,
    '2019-02-03T00:00:00+00',
    'bonus-for-user-tags',
    'calculate',
    10
);
