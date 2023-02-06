
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-dispatch-experiment',
    0,
    '2021-01-01T00:00:00+00',
    'calculate',
    '
    let experiments = order_context.dispatch_experiments;
    var diff = 0;
    if ("dispatch_settings_test_experiment" in experiments)
    {
      diff += experiments["dispatch_settings_test_experiment"]["score"];
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
    'bonus-for-dispatch-experiment',
    'calculate',
    1
);
