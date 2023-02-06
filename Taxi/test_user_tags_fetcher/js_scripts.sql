
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-user-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
    if (order_context.user_tags) {
        let bonus = 0;
        if (order_context.user_tags.includes(`some_user_tag_1`)
            && order_context.user_tags.includes(`some_user_tag_2`)) {
            bonus += 100;
        }
        if (order_context.user_tags.includes(`some_user_tag_3`)
            && order_context.user_tags.includes(`some_user_tag_4`)) {
            bonus += 10;
        }
        return bonus;
    }
    return 0;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-user-tags',
    'calculate',
    1
);
