INSERT INTO moderation.feedback_answer_retrieve_state DEFAULT VALUES;

INSERT INTO eats_feedback.feedback_answer
(id, feedback_id, comment, comment_status)
VALUES
-- Old comments, should not be affected by moderation
(100, 1, 'Old unprocessed comment', 'raw'),
(200, 2, 'Old bad comment', 'rejected'),
(300, 3, 'Old good comment', 'approved'),
(400, 4, NULL, NULL),
-- Newer comments, affected by moderation batch #1
(1100, 11, 'Newer bad comment', 'raw'),
(1200, 12, 'Newer good comment', 'raw'),
-- Newest comments, affected by moderation batch #2
(2100, 21, 'Newest bad comment', 'raw'),
(2200, 22, 'Newest good comment', 'raw');

INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested, predefined_comment_ids, order_nr, comment_status)
VALUES
-- Old comments, should not be affected by moderation
(1, 'Old unprocessed comment', 5, 1, 1, '2021-02-10 12:23', FALSE, '{}', 'ORDER_1', 'raw'),
(2, 'Old bad comment', 4, 1, 1, '2021-02-11 15:11:16', FALSE, '{}', 'ORDER_2', 'rejected'),
(3, 'Old good comment', 4, 1, 1, '2021-02-11 15:11:16', FALSE, '{}', 'ORDER_3', 'approved'),
(4, NULL, 4, 1, 1, '2021-02-11 15:11:16', FALSE, '{}', 'ORDER_4', NULL),
-- Newer comments, affected by moderation batch #1
(11, 'Newer bad comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_11', 'raw'),
(12, 'Newer good comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_12', 'raw'),
-- Newest comments, affected by moderation batch #2
(21, 'Newest bad comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_21', 'raw'),
(22, 'Newest good comment', 3, 1, 1, '2021-02-12 17:11:16', FALSE, '{}', 'ORDER_22', 'raw');
