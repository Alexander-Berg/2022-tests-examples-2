INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, deleted)
  VALUES
    (1, 'return_as_is', 'return ride.price;', 'backend_only', '200ok', 11, 'R(0.0)', '2010-04-04 06:00:00', false),
    (2, 'ternary', 'return (*(ride.price) > 10) ? *(ride.price) : 10;', 'backend_only', '200ok', 12, 'R(0.0)', '2010-04-04 06:00:00', false),
    (3, 'return_70', 'return 70;', 'backend_only', '200ok', 13, 'R(0.0)', '2010-04-04 06:00:00', false),
    (4, 'emit_meow_woof', 'emit("meow", 42) ; emit("woof", 24) ; return ride.price;', 'backend_only', '200ok', 14, 'R(0.0)', '2010-04-04 06:00:00', false),
    (5, 'has_deleted', 'return ride.price;', 'backend_only', '200ok', 15, 'R(0.0)', '2010-04-04 06:00:00', false),
    (6, 'has_deleted', 'return ride.price;', 'backend_only', '200ok', 16, 'R(0.0)', '2010-04-04 06:00:00', true),
    (7, 'other_deleted', 'return ride.price;', 'backend_only', '200ok', 17, 'R(0.0)', '2010-04-04 06:00:00', true),
    (8, 'other_deleted', 'return ride.price;', 'backend_only', '200ok', 18, 'R(0.0)', '2010-04-04 06:00:00', true),
    (9, 'other_deleted', 'return ride.price;', 'backend_only', '200ok', 19, 'R(0.0)', '2010-04-04 06:00:00', true)
;

INSERT INTO price_modifications.rules_drafts
    (rule_id, name, source_code, policy, author, status, errors, ast, updated, pmv_task_id)
  VALUES
    (100, 'return_as_is', 'return ride.price;', 'backend_only', '200ok draft', 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1),
    (101, 'only_draft', 'return ride.price;', 'backend_only', '200ok draft', 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1)
;

INSERT INTO price_modifications.tests
    (test_name, rule_name, backend_variables, trip_details, initial_price, output_price, output_meta, last_result, last_result_rule_id)
    VALUES
    ('test1',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 1),
    ('test2',
     'return_as_is',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 1),
    ('test3',
     'has_deleted',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 6),
    ('test4',
     'only_draft',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 101),
    ('test5',
     'other_deleted',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 7),
    ('test6',
     'other_deleted',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 8),
    ('test7',
     'other_deleted',
     '{}',
     '{ "total_distance": 1, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{}', true, 9)
