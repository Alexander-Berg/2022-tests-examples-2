INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-autoaccept',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    '
    if (candidate_context.autoaccept != undefined
        && candidate_context.autoaccept.enabled) {
        return 600;
    } else {
        return 0;
    }
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-autoaccept',
    'calculate',
    1
);
