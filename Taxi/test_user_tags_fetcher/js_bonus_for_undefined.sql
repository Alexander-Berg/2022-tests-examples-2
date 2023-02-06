INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-user-tags',
    0,
    '2021-10-04T00:00:00+00',
    'calculate',
    '
    if (order_context.user_tags == undefined) {
        return 50;
    }
    return 0;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2021-10-04T00:00:00+00',
    'bonus-for-user-tags',
    'calculate',
    1
);
