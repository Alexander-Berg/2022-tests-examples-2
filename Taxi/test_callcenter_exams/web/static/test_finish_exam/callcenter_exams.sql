INSERT INTO callcenter_exams.exams_pass
(exam_id, variant_id, user_id, cur_question_id, start_time, end_time, score, user_name, group_name, ticket_id)
VALUES
('exam_1', 'v_1', 'user_1', 'q_3', DEFAULT, NULL, 1, '<>&user name', NULL, NULL),
('exam_2', 'v_1', 'user_1', 'q_3', DEFAULT, NULL, 1, 'user name', NULL, NULL),
('exam_3', 'v_2', 'user_2', 'q_2', DEFAULT, NULL, NULL, 'user name', NULL, NULL),
('exam_4', 'v_5', 'user_1', NULL, '2018-09-01 20:00:00-03', '2018-09-01 21:00:00-03', 10, 'user name', NULL, NULL),
('exam_5', 'v_1', 'user_1', 'q_3', DEFAULT, NULL, 1, 'user name', 'vezet_hiring', NULL),
('exam_6', 'v_1', 'user_1', 'q_3', DEFAULT, NULL, 1, NULL, NULL, 'EXAM-123');

INSERT INTO callcenter_exams.exam_variants
(variant_id, questions)
VALUES
('v_1', '{"q_1", "q_2", "q_3"}'),
('v_2', '{"q_1", "q_2", "q_3", "q_4"}');

INSERT INTO callcenter_exams.questions_pass
(exam_id, question_id, result, question_stat, correct_answer)
VALUES
('exam_1', 'q_2', true, DEFAULT, '{}'::jsonb),
('exam_1', 'q_1', DEFAULT, DEFAULT, '{"a":"c"}'::jsonb),
('exam_2', 'q_2', true, DEFAULT, '{}'::jsonb),
('exam_2', 'q_1', DEFAULT, DEFAULT, DEFAULT),
('exam_5', 'q_2', true, DEFAULT, '{}'::jsonb),
('exam_5', 'q_1', DEFAULT, DEFAULT, DEFAULT);


INSERT INTO callcenter_exams.exam_questions
(question_id, audio_link, answer)
VALUES
('q_1', 'link_1', '{"a":"b"}'::jsonb),
('q_2', 'link_2', '{}'::jsonb);
