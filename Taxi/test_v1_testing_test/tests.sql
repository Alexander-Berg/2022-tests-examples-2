INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, deleted)
  VALUES
    (1, 'return_as_is', 'return ride.price;', 'backend_only', '200ok', 11, 'R(0.0)', '2010-04-04 06:00:00', false),
    (4, 'emit_meow_woof', 'return {metadata=["meow": 42, "woof": 24]};', 'backend_only', '200ok', 14, 'R(0.0)', '2010-04-04 06:00:00', false),
    (5, 'has_deleted', 'return ride.price;', 'backend_only', '200ok', 15, 'R(0.0)', '2010-04-04 06:00:00', false),
    (6, 'has_deleted', 'return 1000*ride.price;', 'backend_only', '200ok', 16, 'R(0.0)', '2010-04-04 06:00:00', true)
;

INSERT INTO price_modifications.rules_drafts
    (rule_id, name, source_code, policy, author, approvals_id, status, errors, ast, updated, pmv_task_id)
  VALUES
    (100, 'return_as_is', 'return 2*ride.price;', 'backend_only', '200ok draft', 1, 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1),
    (101, 'only_draft', 'return ride.price;', 'backend_only', '200ok draft', 1, 'success', NULL, 'R(1.1)', '2014-05-04 06:00:00', 1)
;

INSERT INTO price_modifications.tests
    (test_name, rule_name, backend_variables, trip_details, initial_price,
    output_price, output_meta, last_result, last_result_rule_id, price_calc_version)
        VALUES
    ('test_1_can_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}, "user_meta": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, false, 1815, '13'),
     ('test_1_cannot_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}, "user_meta": {}}',
     '{"boarding": 28, "distance": 28, "time": 28, "waiting": 28, "requirements": 28, "transit_waiting": 28, "destination_waiting": 28}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, true, 1815, NULL),
     ('test_1_almost_pass',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}, "user_meta": {}}',
     '{"boarding": 28, "distance": 0, "time": 0, "waiting": 28, "requirements": 0, "transit_waiting": 28, "destination_waiting": 28}',
     '{"boarding": 56, "distance": 0, "time": 5, "waiting": 56, "requirements": 0, "transit_waiting": 56, "destination_waiting": 56}',
     NULL, true, 1815, NULL),
     ('test_with_no_result',
     'return_as_is',
     '{}',
     '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}, "user_meta": {}}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
     NULL, NULL, NULL, NULL)
;
