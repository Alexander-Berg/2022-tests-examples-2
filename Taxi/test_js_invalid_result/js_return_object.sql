
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'ml-dispatch-bonus',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return "A";'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'ml-dispatch-bonus',
    'calculate',
    0
);
