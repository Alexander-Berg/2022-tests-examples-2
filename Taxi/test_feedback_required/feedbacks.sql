INSERT INTO eats_feedback.order_feedbacks
(id, comment, rating, place_id, status, feedback_filled_at, contact_requested, predefined_comment_ids, order_nr, comment_status)
VALUES
(1, NULL, 5, 1, 2, NULL, FALSE, '{}', '210318-000000', NULL),
(2, NULL, 4, 1, 2, NULL, FALSE, '{}', '210318-000001', NULL),
(3, 'Test3', 4, 1, 5, '2021-02-11 15:11:16', FALSE, '{}', '210318-000003', 'approved'),
(12, 'Test4', 3, 1, 3, '2021-02-12 17:11:16', FALSE, '{}', '210318-000004', NULL);
