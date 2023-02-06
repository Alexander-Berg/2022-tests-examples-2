INSERT INTO callcenter_exams.exams_pass
(exam_id, variant_id, user_id, cur_question_id, start_time, end_time, score, user_name, ticket_id)
VALUES
('exam_1', 'v_1', 'user_1', 'q_1', DEFAULT, NULL, 0, 'user name', 'TSC-1'),
('exam_2', 'v_1', 'user_2', 'q_3', DEFAULT, NULL, 0, NULL, 'TSC-2'),
('exam_3', 'v_1', 'user_3', 'q_3', DEFAULT, NULL, 0, 'user name', 'TSC-3'),
('exam_4', 'v_1', 'user_4', 'q_2', DEFAULT, NULL, 0, 'user name', 'TSC-4');

INSERT INTO callcenter_exams.exam_variants
(variant_id, questions)
VALUES
('v_1', '{"q_1", "q_2", "q_3"}');

INSERT INTO callcenter_exams.questions_pass
(exam_id, question_id, result, question_stat)
VALUES
('exam_1', 'q_1', DEFAULT, '{"orderscancel": 1, "other": "info"}'::jsonb),
('exam_2', 'q_3', DEFAULT, '{"orderscancel": 2}'),
('exam_4', 'q_2', DEFAULT, '{"orderscancel": 2}');

INSERT INTO callcenter_exams.exam_questions
(question_id, audio_link, answer)
VALUES
('q_1', 'audio_1', '{"orderscancel": 1, "final_action": "cancel", "other": "other_info"}'::jsonb),
('q_3', 'audio_3', '{"orderscancel": 1}'::jsonb);
