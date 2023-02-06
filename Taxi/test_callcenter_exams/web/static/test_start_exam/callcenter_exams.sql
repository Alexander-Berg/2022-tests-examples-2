INSERT INTO callcenter_exams.exams_pass
(exam_id, variant_id, user_id, cur_question_id, start_time, end_time, score, user_name)
VALUES
('exam_4', 'v_2', 'user_3', 'q_1', DEFAULT, NULL, NULL, 'user name'),
('exam_1', 'v_2', 'many_attempts_user', 'q_1', now() - (1 ||' hours')::interval,
 now() - (1 ||' hours')::interval, 1, 'user name'),
('exam_2', 'v_2', 'many_attempts_user', 'q_1', now() - (2 ||' hours')::interval,
 now(), 0, 'user name');

INSERT INTO callcenter_exams.exam_variants
(variant_id, questions)
VALUES
('v_1', '{"q_1", "q_2", "q_3"}'),
('v_2', '{"q_1", "q_2", "q_3", "q_4"}');


INSERT INTO callcenter_exams.exam_questions
(question_id, audio_link, answer)
VALUES
('q_1', 'link_1', '{"a":"b"}'::jsonb),
('q_2', 'link_2', '{}'::jsonb);
