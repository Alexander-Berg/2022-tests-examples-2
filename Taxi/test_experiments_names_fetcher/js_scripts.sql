
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-experiments-names',
    0,
    '2021-01-01T00:00:00+00',
    'calculate',
    '
    let experiments_names = order_context.experiments_names;
    var diff = 0;
    if (experiments_names.includes("dispatch_settings_test_experiment"))
    {
      diff += 10;
    }

    if (experiments_names.includes("metadata_test_experiment"))
    {
      diff += 100;
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
    'bonus-for-experiments-names',
    'calculate',
    1
);
