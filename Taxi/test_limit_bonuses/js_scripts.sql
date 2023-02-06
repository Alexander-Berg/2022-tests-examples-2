
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-driver-tags',
    0,
    '2019-02-03T00:00:00+00',
    'calculate',
    'return 100 * candidate_context.tags.length;'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2019-02-03T00:00:00+00',
    'bonus-for-driver-tags',
    'calculate',
    1
);
