INSERT INTO eats_place_rating.feedback_answer_templates (
    template_id, 
    partner_id,
    template
) VALUES
(5, 11, '1234567890'),
(6, 11, 'zxcvbnm'),
(3, 11, 'qwerty'),
(4, 11, 'asdf'),
(2, 12, 'qwerty'),
(1, 11, 'abacaba');

SELECT setval(pg_get_serial_sequence(
    'eats_place_rating.feedback_answer_templates',
    'template_id'), 10);
