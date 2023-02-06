INSERT INTO callcenter_exams.exams_pass
(exam_id, variant_id, user_id, cur_question_id, start_time, end_time, score, user_name)
VALUES
('exam_1', 'v_1', 'user_1', 'q_1', DEFAULT, NULL, NULL, 'user name'),
('exam_2', 'v_2', 'user_2', 'q_2', DEFAULT, NULL, NULL, 'user name'),
('exam_3', 'v_5', 'user_1', NULL, '2018-09-01 20:00:00-03', '2018-09-01 21:00:00-03', 10, 'user name'),
('exam_4', 'v_2', 'user_3', 'q_1', DEFAULT, NULL, NULL, 'user name'),
('exam_5', 'v_2', 'user_4', 'q_2', DEFAULT, NULL, NULL, 'user name'),
('expired_exam', 'v_1', 'user_5', 'q_1', '2019-09-11 20:00:00-03', NULL, NULL, 'user name'),
('exam_6', 'v_4', 'user_5', NULL, '2018-09-01 20:00:00-03', '2018-09-01 21:00:00-03', 5, 'user name');

INSERT INTO callcenter_exams.mock_responses
(question_id, handler, answer, is_default)
VALUES
('q_1', 'expecteddestinations', '"q_1_expecteddestinations_resp"'::jsonb, FALSE),
('q_1', 'expectedpositions', '"q_1_expectedpositions_resp"'::jsonb, FALSE),
('q_1', 'orderscommit', '"q_1_orderscommit_resp"'::jsonb, FALSE),
('q_1', 'orderssearch', '"q_1_orderssearch_resp"'::jsonb, FALSE),
('q_1', 'paymentmethods', '"q_1_paymentmethods_resp"'::jsonb, FALSE),
('q_1', 'profile', '"q_1_profile_resp"'::jsonb, FALSE),
('q_1', 'zoneinfo', '"q_1_zoneinfo_resp"'::jsonb, FALSE),
('q_1', 'nearestzone', '"q_1_nearestzone_resp"'::jsonb, FALSE),
('q_1', 'zonaltariffdescription', '"q_1_zonaltariffdescription_resp"'::jsonb, FALSE),
('q_1', 'nearestposition', '"q_1_nearestposition_resp"'::jsonb, FALSE),
('q_1', 'ordersestimate', '"q_1_ordersestimate_resp"'::jsonb, FALSE),
('q_1', 'ordersdraft', '"q_1_ordersdraft_resp"'::jsonb, FALSE),
('q_1', 'availability', '"q_1_availability_resp"'::jsonb, FALSE),
('default', 'expecteddestinations', '"default_expecteddestinations_resp"'::jsonb, FALSE),
('q_2', 'expecteddestinations', NULL, TRUE),
('real_question', 'orderssearch', '{"orders":[{"request":{"class": "econom", "route": [{"geopoint": [55.753219, 37.62251]}], "requirements": {}}, "status": "search", "payment": {"type": "cash", "payment_method_id": "cash"}}]}'::jsonb, FALSE),
('real_question', 'paymentmethods', '{"methods": [{"id": "cash", "type": "cash", "label": "Наличные", "can_order": true, "hide_user_cost": false, "zone_available": true}, {"id": "corp-89c43fa2faab4518849ae29fdc25926d", "type": "corp", "label": "Команда Яндекс.Такси", "can_order": true, "cost_center": "", "description": "Осталось 2955 из 6000 руб.", "hide_user_cost": false, "zone_available": true}], "last_payment_method": {"id": "corp-89c43fa2faab4518849ae29fdc25926d", "type": "corp"}, "default_payment_method_id": "corp"}'::jsonb, FALSE),
('default', 'orderssearch', '{"orders":[]}'::jsonb, FALSE);

INSERT INTO callcenter_exams.exam_variants
(variant_id, questions)
VALUES
('v_1', '{"q_1", "q_2", "q_3"}'),
('v_2', '{"q_1", "q_2", "q_3", "q_4"}');

INSERT INTO callcenter_exams.questions_pass
(exam_id, question_id, result, question_stat)
VALUES
('exam_1', 'q_1', DEFAULT, DEFAULT);

INSERT INTO callcenter_exams.exam_questions
(question_id, audio_link, answer)
VALUES
('q_1', 'link_1', '"1"'::jsonb),
('q_2', 'link_2', '"2"'::jsonb),
('q_3', 'link_3', '"3"'::jsonb),
('q_4', 'link_4', '"4"'::jsonb),
('q_5', 'link_5', '{"ordersdraft": {"payment": {"type": "cash", "payment_method_id": "cash"}, "route": [], "class": ["econom"], "requirements": {}}}'::jsonb),
('real_question', 'real_question_link', '{}'::jsonb);
