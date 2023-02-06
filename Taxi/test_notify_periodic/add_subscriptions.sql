INSERT INTO eats_surge_notify.subscriptions(id, eater_id, session_id, place_id, place_slug, place_name, place_business_type, locale, surge_level, location, region_id, device_id, personal_phone_id, idempotency_token, delivery_time, created_at, updated_at)
VALUES
    ('1', '1000', 'session-id-1', '49000', 'slug', 'name', 'restaurant', 'ru', 1, ('1,1'), 1, 'device_id', 'phone_id', '1.49000', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00'),
    ('2', '1001', 'session-id-2', '49001', 'slug', 'name', 'restaurant', 'ru', 2, ('1,1'), 1, 'device_id', 'phone_id', '2.49001', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00'),
    ('3', '1002', 'session-id-3', '49002', 'slug', 'name', 'restaurant', 'ru', 3, ('1,1'), 1, 'device_id', 'phone_id', '3.49002', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00'),
    ('4', '1003', 'session-id-4', '49003', 'slug', 'name', 'restaurant', 'ru', 4, ('1,1'), 1, 'device_id', 'phone_id', '4.49003', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00'),
    ('5', '1004', 'session-id-5', '49004', 'slug', 'name', 'restaurant', 'ru', 5, ('1,1'), 1, 'device_id', 'phone_id', '5.49004', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00'),
    ('6', '1005', 'session-id-6', '49005', 'slug', 'name', 'restaurant', 'ru', 6, ('1,1'), 1, 'device_id', 'phone_id', '6.49005', null, '2019-12-31T23:59:00+00:00', '2019-12-31T23:59:00+00:00'),
    ('7', '1006', 'session-id-7', '49006', 'unavailable_place_slug', 'name', 'restaurant',  'ru', 7, ('1,1'), 1, 'device_id', 'phone_id', '7.49006', null, '2019-12-31T23:58:59+00:00', '2019-12-31T23:58:59+00:00');
