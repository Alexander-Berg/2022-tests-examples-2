INSERT INTO taxi_fraud.retrieve_state DEFAULT VALUES;

INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested, predefined_comment_ids, order_nr, fraud_skip)
VALUES
(1, 'Old bad comment', 4, 1, 5, '2021-02-11 15:11:16', FALSE, '{}', '111111-100007', TRUE),
(2, 'Old bad comment', 4, 1, 3, '2021-02-11 15:11:16', FALSE, '{}', '111111-100008', TRUE);
