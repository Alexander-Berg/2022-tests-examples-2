INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, deleted)
  VALUES
    (1, 'return_as_is', 'return ride.price;', 'backend_only', '200ok', 11, 'R(0.0)', '2010-04-04 06:00:00', false),
    (4, 'emit_meow_woof', 'emit("meow", 42) ; emit("woof", 24) ; return ride.price;', 'backend_only', '200ok', 14, 'R(0.0)', '2010-04-04 06:00:00', false),
    (5, 'has_deleted', 'return ride.price;', 'backend_only', '200ok', 15, 'R(0.0)', '2010-04-04 06:00:00', false),
    (6, 'has_deleted', 'return 1000*ride.price;', 'backend_only', '200ok', 16, 'R(0.0)', '2010-04-04 06:00:00', true)
;

INSERT INTO price_modifications.rules_drafts
    (rule_id, name, source_code, policy, author, status, errors, ast, updated, pmv_task_id)
  VALUES
    (100, 'return_as_is', 'return 2*ride.price;', 'backend_only', '200ok draft', 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1),
    (101, 'only_draft', 'return 3*ride.price;', 'backend_only', '200ok draft', 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1)
;

INSERT INTO price_modifications.tests
    (test_name, rule_name, backend_variables, trip_details, initial_price,
    output_price, output_meta, last_result, last_result_rule_id)
        VALUES
    ('test_1_can_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, false, 1815),
     ('test_1_cannot_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 28, "distance": 28, "time": 28, "waiting": 28, "requirements": 28, "transit_waiting": 28, "destination_waiting": 28}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, true, 1815),
     ('test_draft_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 28, "distance": 0, "time": 0, "waiting": 28, "requirements": 0, "transit_waiting": 28, "destination_waiting": 28}',
     '{"boarding": 56, "distance": 0, "time": 0, "waiting": 56, "requirements": 0, "transit_waiting": 56, "destination_waiting": 56}',
     NULL, true, 1815),
     ('test_rule_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 28, "distance": 0, "time": 0, "waiting": 28, "requirements": 0, "transit_waiting": 28, "destination_waiting": 28}',
     '{"boarding": 28, "distance": 0, "time": 0, "waiting": 28, "requirements": 0, "transit_waiting": 28, "destination_waiting": 28}',
     NULL, true, 1815),
     ('test_1_can_pass',
     'only_draft',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, NULL, NULL),
     ('test_2_can_pass',
     'only_draft',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 1, "distance": 2, "time": 3, "waiting": 4, "requirements": 5, "transit_waiting": 6, "destination_waiting": 7}',
     '{"boarding": 3, "distance": 6, "time": 9, "waiting": 12, "requirements": 15, "transit_waiting": 18, "destination_waiting": 21}',
     NULL, NULL, NULL),
     ('test_1_cannot_pass',
     'only_draft',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 1, "distance": 2, "time": 3, "waiting": 4, "requirements": 5, "transit_waiting": 6, "destination_waiting": 7}',
     '{"boarding": 0, "distance": 6, "time": 9, "waiting": 12, "requirements": 15, "transit_waiting": 18, "destination_waiting": 21}',
     NULL, NULL, NULL),
     ('test_2_cannot_pass',
     'only_draft',
     '{"surge_params": 42}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 1, "distance": 2, "time": 3, "waiting": 4, "requirements": 5, "transit_waiting": 6, "destination_waiting": 7}',
     '{"boarding": 3, "distance": 6, "time": 9, "waiting": 12, "requirements": 15, "transit_waiting": 18, "destination_waiting": 21}',
     NULL, NULL, NULL),
     ('test_3_cannot_pass',
     'only_draft',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
     '{"boarding": 1, "distance": 2, "time": 3, "waiting": 4, "requirements": 5, "transit_waiting": 6, "destination_waiting": 7}',
     '{"boarding": 3, "distance": 6, "time": 9, "waiting": 12, "requirements": 15, "transit_waiting": 18, "destination_waiting": 21}',
     '{"fake_meta": 73}',
     NULL, NULL)
;
