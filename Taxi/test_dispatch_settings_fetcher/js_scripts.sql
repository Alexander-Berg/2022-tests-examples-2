
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'bonus-for-dispatch-settings',
    0,
    '2021-01-01T00:00:00+00',
    'calculate',
    '
    let dispatch_settings = order_context.dispatch_settings;
    var diff = 0;
    if ("MAX_ROBOT_TIME" in dispatch_settings)
    {
      diff += dispatch_settings["MAX_ROBOT_TIME"];
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
    'bonus-for-dispatch-settings',
    'calculate',
    1
);
