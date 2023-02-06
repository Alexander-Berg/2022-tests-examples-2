INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-eats-user-tags',
    0,
    '2021-10-04T00:00:00+00',
    'calculate',
    '
    if (order_context.eats_user_tags
        && order_context.eats_user_tags.constructor == Array
        && order_context.eats_user_tags.length == 0) {
        return 172;
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
    'bonus-for-eats-user-tags',
    'calculate',
    1
);
