
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-eats-place-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
    if (order_context.eats_place_tags) {
        let bonus = 0;
        if (order_context.eats_place_tags.includes(`some_place_tag_1`)
            && order_context.eats_place_tags.includes(`some_place_tag_2`)) {
            bonus += 100;
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
    'bonus-for-eats-place-tags',
    'calculate',
    1
);
