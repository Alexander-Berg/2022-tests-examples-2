INSERT INTO passenger_feedback.current_questions (
    udid,
    current_question_id,
    answer_ids,
    answer_values,
    updated_at
)
VALUES (
    'udid00',
    'q_1',
    '{negative, positive, positive}',
    '{0, 1, 1}',
    '2018-08-10T21:01:30+0300'
),
(
    'udid00',
    'q_2',
    '{negative, positive, positive}',
    '{0, 1, 1}',
    '2018-08-10T21:01:30+0300'
),
(
    'udid01',
    'q_1',
    '{positive}',
    '{1}',
    '2018-08-10T21:01:30+0300'
),(
    'udid02',
    'pleasent music',
    '{negative}',
    '{0}',
    '2018-08-10T21:01:30+0300'
),
(
    'udid03',
    'q_1',
    '{negative, positive}',
    '{0, 1}',
    '2018-08-10T21:01:30+0300'
);

INSERT INTO passenger_feedback.questions_history (
    udid,
    question_id,
    answer_ids,
    answer_values,
    updated_at
)
VALUES (
    'udid02',
    'pleasent music',
    '{positive,positive}',
    '{1, 1}',
    '2018-08-10T20:01:30+0300'
)
