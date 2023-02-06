INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, extra_return, startrek_ticket)
  VALUES
(1001, 'one', 'return (1 / *ride.price) * ride.price;', 'backend_only', '200ok', 11, 'CR(boarding=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2010-04-04 06:00:00', ARRAY['ex1', 'ex2'], 'EFFICIENCYDEV-17020'),
(1002, 'two', 'return (2 / *ride.price) * ride.price;', 'backend_only', '200ok', 22, 'CR(boarding=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(2.000000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2011-04-04 06:00:00', ARRAY['ex1'], NULL),
(1003, 'three', 'return (3 / *ride.price) * ride.price;', 'both_side', '200ok', 33, 'CR(boarding=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(3.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2012-04-04 06:00:00', ARRAY['ex1', 'ex2'], 'EFFICIENCYDEV-17020-1'),
(1004, 'four', 'return (4 / *ride.price) * ride.price;', 'backend_only', '200ok', 44, 'CR(boarding=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(4.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2013-04-04 06:00:00', ARRAY['ex1', 'ex3'], 'EFFICIENCYDEV-17020-1'),
(1005, 'five', 'return (5 / *ride.price) * ride.price;', 'taximeter_only', '200ok', 55, 'CR(boarding=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(5.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-04-04 06:00:00', ARRAY['ex1'], NULL)
;

INSERT INTO price_modifications.rules_drafts
    (rule_id, name, source_code, policy, author, status, approvals_id, errors, ast, updated, pmv_task_id)
  VALUES
(1006, 'a_draft', 'return (1.1 / *ride.price) * ride.price;', 'backend_only', '200ok draft', 'running', NULL, NULL, 'CR(boarding=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-05-04 06:00:00', 1),
(1007, 'one', 'return (2.2 / *ride.price) * ride.price;', 'backend_only', '200ok draft', 'failure', NULL, 'error message', 'CR(boarding=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(2.20000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-06-04 06:00:00', 2), /* not "one_draft" for test with same names */
(1008, 'two_draft', 'return (3.3 / *ride.price) * ride.price;', 'backend_only', '200ok draft', 'failure', 2, 'error message', 'CR(boarding=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(3.30000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-07-04 06:00:00', 3),
(1009, 'three_draft', 'return (4.4 / *ride.price) * ride.price;', 'backend_only', '200ok draft', 'failure', 2, 'error message', 'CR(boarding=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(4.40000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-08-04 06:00:00', 4),
(1010, 'four_draft', 'return (5.5 / *ride.price) * ride.price;', 'both_side', '200ok draft', 'failure', 2, 'error message', 'CR(boarding=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(5.50000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-09-04 06:00:00', 5),
(1011, 'five_draft', 'return (6.6 / *ride.price) * ride.price;', 'taximeter_only', '200ok draft', 'failure', 2, 'error message', 'CR(boarding=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(6.60000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2014-10-04 06:00:00', 6)
;

INSERT INTO price_modifications.tests
(test_name, rule_name, backend_variables, trip_details, initial_price, output_price, output_meta, last_result, last_result_rule_id)
VALUES
(
    'test_with_some_previous_result',
    'one',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    true,
    1006
),
(
    'test_no_previous_result',
    'one',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    null,
    null
),
(
    'test_with_false_previous_result_two',
    'two',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    false,
    1002
),
(
    'test_with_true_previous_result_three',
    'three',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    true,
    1003
),
(
    'test_with_true_previous_result_three_draft',
    'three_draft',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    true,
    1009
),
(
    'test_with_true_previous_result_three_draft_1',
    'three_draft',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    true,
    1006
),
(
    'test_with_false_previous_result_four',
    'four',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    false,
    1004
),
(
    'test_with_true_previous_result_four',
    'four',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    true,
    1004
),
(
    'test_with_false_previous_result_five',
    'five',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    false,
    1005
),
(
    'test_no_previous_result_five',
    'five',
    '{}',
    '{ "total_distance": 0, "total_time": 2, "waiting_time": 0, "waiting_in_transit_time": 0, "waiting_in_destination_time": 0, "user_options": {}}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{"boarding": 0, "distance": 0, "time": 0, "waiting": 0, "requirements": 0, "transit_waiting": 0, "destination_waiting": 0}',
    '{}',
    null,
    null
)
;
