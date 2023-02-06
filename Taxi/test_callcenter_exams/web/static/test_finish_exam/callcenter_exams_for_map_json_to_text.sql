INSERT INTO callcenter_exams.exams_pass
(exam_id, variant_id, user_id, cur_question_id, start_time, end_time, score, user_name, group_name, ticket_id)
VALUES
('exam_7', 'v_1', 'user_1', 'q_3', DEFAULT, NULL, 1, 'user name', NULL, 'EXAM-123'),
('exam_8', 'v_2', 'user_1', 'q_12', DEFAULT, NULL, 1, 'user name', NULL, 'EXAM-123');

INSERT INTO callcenter_exams.exam_variants
(variant_id, questions)
VALUES
('v_1', '{"q_1", "q_2", "q_3"}'),
('v_2', '{"q_10", "q_11", "q_12"}');

INSERT INTO callcenter_exams.questions_pass
(exam_id, question_id, result, question_stat, correct_answer)
VALUES
('exam_7', 'q_2', true, DEFAULT, DEFAULT),
('exam_7', 'q_1', DEFAULT, DEFAULT, '{"final_action": "become_driver_form"}'::jsonb),
('exam_8', 'q_11', true, DEFAULT, DEFAULT),
('exam_8', 'q_10', DEFAULT, DEFAULT, '{"ordersdraft": {"class": ["econom"], "route": [{"city": "Краснодар", "type": "address", "fullname": "Россия, Краснодар, микрорайон Центральный, улица Дмитриевская Дамба, 1", "geopoint": [38.989902, 45.028145], "short_text": "улица Дмитриевская Дамба, 1"}, {"city": "Краснодар", "type": "address", "fullname": "Россия, Краснодар, Российская улица, 267/6", "geopoint": [39.007536, 45.091857], "short_text": "Российская улица, 267/6"}], "payment": {"type": "cash", "payment_method_id": "cash"}, "requirements": {}}, "final_action": "driver_ivr_call"}'::jsonb);


INSERT INTO callcenter_exams.exam_questions
(question_id, audio_link, answer)
VALUES
('q_1', 'link_1', '{"final_action": "become_driver_form"}'::jsonb),
('q_2', 'link_2', '{}'::jsonb),
('q_10', 'link_1', '{"final_action": "become_driver_form"}'::jsonb),
('q_11', 'link_2', '{}'::jsonb);
