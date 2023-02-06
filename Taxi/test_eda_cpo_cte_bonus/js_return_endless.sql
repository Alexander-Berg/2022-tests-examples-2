
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    0,
    'eda_cpo_cte_bonus',
    0,
    '2022-06-17T00:00:00+00',
    'calculate',
    'while (true) {};'
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    0,
    '2022-06-17T00:00:00+00',
    'eda_cpo_cte_bonus',
    'calculate',
    0
);
