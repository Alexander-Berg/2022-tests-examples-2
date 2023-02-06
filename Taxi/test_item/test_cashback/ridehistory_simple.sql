INSERT INTO ridehistory.user_index
    (order_id, phone_id, user_uid,
     payment_tech_type, payment_method_id, is_hidden,
     order_created_at, seen_unarchived_at)
VALUES
    ('1', '777777777777777777777777', '12345',
     'coop_account', 'family-666', FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('3', '777777777777777777777776', '1234',
     'coop_account', 'family-666', FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00'),
    ('5', '777777777777777777777776', '1234',
     'yandex_card', 'family-666', FALSE,
     '2017-09-08 00:00:00.00+00:00', '2100-09-08 00:00:00.00+00:00')
