INSERT INTO eats_feedback.order_feedbacks
(comment, rating, place_id, status, feedback_filled_at, contact_requested,
predefined_comment_ids, order_nr, comment_status, order_delivery_type)
VALUES('NEVER MIND', 4, 1, 5, '2021-05-01 12:23', FALSE, '{15, 9}', 'ORDER_1', 'raw', 'our_delivery');

INSERT INTO eats_feedback.order_feedbacks
(comment, rating, place_id, status, feedback_filled_at, contact_requested,
predefined_comment_ids, order_nr, comment_status, order_delivery_type)
VALUES('GOOD FOOD :)', 5, 1, 5, '2021-05-04 15:11:16', FALSE, '{9}', 'ORDER_2', 'approved', 'marketplace'),
      ('DELICIOUS', 5, 3, 5, '2021-05-05 15:28:16', FALSE, '{}', 'ORDER_3', 'approved', NULL),
      ('NICE', 5, 4, 5, '2021-05-08 12:00:00', FALSE, '{}', 'ORDER_4', 'approved', NULL),
      ('BAD', 2, 4, 5, '2021-05-09 12:00:00', FALSE, '{}', 'ORDER_5', 'approved', NULL);
