INSERT INTO eats_feedback.order_feedbacks
(comment, rating, place_id, status, feedback_filled_at, contact_requested,
 predefined_comment_ids, order_nr, comment_status, order_delivery_type)
VALUES ('FRESH FOOD FOOD :)', 5, 1, 5, '2021-02-10 13:11:16', FALSE, '{9}', 'ORDER_4', 'approved', 'marketplace'),
       ('GOOD FOOD :)', 5, 1, 5, '2021-02-10 15:11:16', FALSE, '{9}', 'ORDER_2', 'approved', 'marketplace'),
       ('BAD FOOD :(', 5, 1, 5, '2021-02-10 14:11:16', FALSE, '{9}', 'ORDER_3', 'approved', 'marketplace'),
       ('NEVER MIND', 4, 1, 5, '2021-02-10 16:11:16', FALSE, '{15, 9}', 'ORDER_1', 'raw', 'our_delivery');
