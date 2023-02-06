INSERT INTO price_modifications.rules
(rule_id, previous_version_id, name, description, source_code, policy, author, approvals_id, pmv_task_id, deleted, ast, startrek_ticket)
VALUES
    (1, null, 'rule_with_long_story', 'description', 'return ride.price;', 'both_side', 'gman', 1001, 5, true, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', null),
    (2, null, 'rule_with_line_story', 'description2', 'return ride.price*2;', 'both_side', 'gman', 1002, 5, true, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', null),
    (3, 2, 'rule_with_line_story', 'description3', 'return ride.price*3;', 'both_side', 'gman', 1003, 5, true, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', 'EFFICIENCYDEV-16339'),
    (4, 3, 'rule_with_line_story', 'description4', 'return ride.price*4;', 'both_side', 'gman', 1004, 5, false, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', null),
    (5, 1, 'rule_with_long_story', 'description5', 'return ride.price*5;', 'both_side', 'gman', 1005, 5, false, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', null),
    (6, null, 'rule_with_empty_history', 'description6', 'return ride.price*6;', 'both_side', 'gman', 1006, 5, false, 'CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),metadata=NT(),requirements=51.000000,time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))', null)
;


