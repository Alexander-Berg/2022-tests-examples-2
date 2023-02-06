
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'dynamic-bonus-for-reposition',
    0,
    '2019-02-03T00:00:00+00',
    'filter',
    'return -1;'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2019-02-03T00:00:00+00',
    'dynamic-bonus-for-reposition',
    'filter',
    0
);
