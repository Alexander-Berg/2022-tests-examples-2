INSERT INTO eats_feedback.feedback_answer
(feedback_id, comment, comment_status, coupon, coupon_value, coupon_percent,
 coupon_limit, coupon_expire_at, coupon_currency)
VALUES(1, 'comment', 'raw', NULL, NULL, NULL, NULL, NULL, NULL),
      (1, 'comment', 'rejected', NULL, NULL, NULL, NULL, NULL, NULL),
      (2, 'comment', 'approved', 'COUPON', NULL, 10, 1999.99, '2022-03-08 23:59', 'RUB');
