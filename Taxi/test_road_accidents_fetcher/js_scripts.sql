
/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, updated, type, content)
VALUES
(
    1,
    'penalty-for-road-accidents',
    0,
    '2021-09-17T00:00:00+00',
    'calculate',
    '
    const penalty = 60.0;
    
    // const driver_safety_tag = `driver_safety_group_score_over_cut_off`;
    // const is_dangerous_driver = candidate_context.tags.includes(driver_safety_tag);
    
    const is_dangerous_driver = candidate_context.uuid === "uuid0";
    
    if (
        is_dangerous_driver && 
        order_context.road_accidents && 
        order_context.road_accidents.reduce((acc,val) => acc+val, 0) > 10
    ) {
        return penalty;
    }
    return 0;
    '
);

INSERT INTO scripts.active_scripts
(id, updated, bonus_name, type, script_id)
VALUES
(
    2,
    '2021-09-17T00:00:00+00',
    'penalty-for-road-accidents',
    'calculate',
    1
);
