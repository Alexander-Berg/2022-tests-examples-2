INSERT INTO order_log.order_log (order_id, updated, can_be_archived)
VALUES ('id-1-grocery', '2020-02-20T15:55:01.4183+03:00'::timestamptz, false),
('id-2-grocery', '2020-02-20T15:55:01.4183+03:00'::timestamptz, true),
('id-3-grocery', '2020-02-28T15:55:01.4183+03:00'::timestamptz, false),
('id-4-grocery', '2020-02-28T15:55:01.4183+03:00'::timestamptz, true);
