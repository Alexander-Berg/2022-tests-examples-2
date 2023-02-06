INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-candidate-context-experiments',
    0,
    '2021-01-01T00:00:00+00',
    'calculate',
    '
    let experiments_names = candidate_context.matched_experiments;
    var diff = 0;

    for (var value in experiments_names) {
        if ("score" in experiments_names[value]) {
            diff += experiments_names[value]["score"];
        }
    }

    return diff;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2021-01-01T00:00:00+00',
    'bonus-for-candidate-context-experiments',
    'calculate',
    1
);
