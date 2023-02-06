INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-points-surge-values',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
    if (order_context.batch_properties_surge_values.length != 0) {
        return 100;
    }
    return 0;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    3,
    '2019-02-03T00:00:00+00',
    'bonus-for-points-surge-values',
    'calculate',
    1
);
