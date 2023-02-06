INSERT INTO users
    (id, guid, first_name, last_name, msisdn, avatar, language_id, number_of_trips)
VALUES
    (5678, '9373F48B-C6B4-4812-A2D0-413F3A000006', 'first_name', 'last_name', 'msisdn', 'avatar', 1, 0),
    (3456, '9373F48B-C6B4-4812-A2D0-413F3A000007', 'first_name', 'last_name', 'msisdn', 'avatar', 1, 0);


INSERT INTO devices
    (user_guid, device_uuid, device_os, device_os_version, build_number, is_store_build, build_number_name, device_name, created_at)
VALUES
    ('9373F48B-C6B4-4812-A2D0-413F3A000006', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00'),
    ('9373F48B-C6B4-4812-A2D0-413F3A000007', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00');


INSERT INTO drivers
    (id, driver_id, guid, avg_rating, current_balance, city_id, country_id, partner_id, has_vehicle, internal_comments, driver_data, reg_step, number_of_trips, driver_status, created_at, updated_at, moderation_data, sign_up_date, first_bid_created, first_order_created, is_for_testing)
VALUES
    (582, 1449, '9373F48B-C6B4-4812-A2D0-413F3A000006', 0.00, 0.00, null, 2, null, '0', '', null, '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0'),
    (583, 1450, '9373F48B-C6B4-4812-A2D0-413F3A000007', 0.00, 0.00, null, 2, null, '0', '', null, '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0');
