INSERT INTO ridehistory.user_index
    (order_id, phone_id, user_uid,
     payment_tech_type, payment_method_id, is_hidden,
     order_created_at, seen_unarchived_at)
VALUES
    ('1', '777777777777777777777777', '12345',
     'coop_account', 'family-666', FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('3', '777777777777777777777776', '1234',
     'coop_account', 'family-666', TRUE,
     '2017-09-07 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('4', '777777777777777777777776', '1234',
     'coop_account', 'family-666', TRUE,
     '2017-09-07 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('wo_db_id', '777777777777777777777777', '12345',
     NULL, NULL, FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('corp', '777777777777777777777777', '12345',
     'corp', NULL, FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('some_order', '777777777777777777777777', '12345',
     'cash', NULL, FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00');

INSERT INTO ridehistory.hidden_orders
    (order_id, phone_id, user_uid,
     payment_tech_type, payment_method_id)
VALUES
    ('4', '777777777777777777777777', '12345',
     'coop_account', 'family-666'),
    ('5', '777777777777777777777777', '12345',
     'coop_account', 'family-666');
