INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested,
predefined_comment_ids, order_nr, comment_status)
VALUES

-- previously filled feedback
(100, 'Previously filled feedback', 4, 1, 5, '2021-02-10 12:23', FALSE, '{1,3}', '100', 'raw'),

-- previously cancelled feedback
(101, NULL, NULL, 1, 3, NULL, FALSE, '{}', '101', NULL);

-- id-s 100+ are reserved for feedbacks created in tests
