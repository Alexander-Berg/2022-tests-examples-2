INSERT INTO taxi_fraud.retrieve_state DEFAULT VALUES;

INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested, predefined_comment_ids, order_nr, fraud_skip)
VALUES
-- Old comments, should not be affected
(1, 'Old bad comment', 4, 1, 1, '2021-02-11 15:11:16', FALSE, '{}', 'ORDER_1', TRUE),
(2, 'Old good comment', 4, 1, 1, '2021-02-11 15:11:16', FALSE, '{}', 'ORDER_2', FALSE),
-- Newer comments, changed at 1619000100
(11, 'Newer bad comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_11', DEFAULT),
(12, 'Newer good comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_12', DEFAULT),
-- Newest comments, changed at 1619000200
(21, 'Newest bad comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_21', DEFAULT),
(22, 'Newest good comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_22', DEFAULT);
