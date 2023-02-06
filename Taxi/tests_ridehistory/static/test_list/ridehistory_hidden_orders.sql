INSERT INTO ridehistory.user_index
    (order_id, phone_id, user_uid, order_created_at, seen_unarchived_at, is_hidden)
VALUES
    ('77777777777777777777777777777777', '777777777777777777777777', '12345',
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00', FALSE),
    ('77777777777777777777777777777776', '777777777777777777777777', '12345',
     '2017-09-07 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00', TRUE);

INSERT INTO ridehistory.hidden_orders
    (order_id, phone_id, user_uid)
VALUES
    ('yt_order1', '777777777777777777777777', '12345'),
    ('yt_order2', '777777777777777777777777', '12345');
