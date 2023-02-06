INSERT INTO users
    (id, guid, first_name, last_name, msisdn, avatar, language_id)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'first_name', 'last_name', 'msisdn1234', 'avatar', 1),
    (5678, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', 'first_name', 'last_name', 'msisdn5678', 'avatar', 1),
    (3456, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (3457, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (1450, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Z', 'first_name', 'last_name', 'msisdn', null, 1),
    (1451, '9373F48B-C6B4-4812-A2D0-413F3AFBAD4Z', 'first_name', 'last_name', 'msisdn', null, 1);

INSERT INTO devices
    (user_guid, device_uuid, device_os, device_os_version, build_number, is_store_build, build_number_name, device_name, created_at)
VALUES
    ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00'),
    ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00'),
    ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00'),
    ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00'),
    ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5Z', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', '', '2020-04-29 10:10:00');

INSERT INTO drivers
    (id, driver_id, guid, avg_rating, current_balance, city_id, country_id, partner_id, has_vehicle, internal_comments, driver_data, reg_step, number_of_trips, driver_status, created_at, updated_at, moderation_data, sign_up_date, first_bid_created, first_order_created, is_for_testing)
VALUES
    (582, 1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 0.00, 0.00, null, 12, null, '0', '', null, '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0'),
    (583, 1448, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 5.00, 0.00, null, 12, null, '0', '', null, '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0');

INSERT INTO vehicles
    (id, driver_id, plate_number, vehicle_image, vehicle_model_id, vehicle_color_id, vehicle_status, created_at, updated_at, vehicle_type_id)
VALUES
    (97, 1449, '77LL777', 'https://api-tada.helix.am/images/drivers/5f3ba8ba-e9b3-4677-9c5f-39da918589f1/vehicle_photo/1570697352.jpeg', 2, 3, 'pending', '2019-10-10 08:49:15', '2019-10-10 08:49:15', null),
    (98, 1448, '77LL777', 'https://api-tada.helix.am/images/drivers/5f3ba8ba-e9b3-4677-9c5f-39da918589f1/vehicle_photo/1570697352.jpeg', 2, 3, 'pending', '2019-10-10 08:49:15', '2019-10-10 08:49:15', null);

INSERT INTO vehicle_colors
    (id, hex_color, custom_color_image, sort_order, show_status, created_at, updated_at, created_admin_id, created_admin_ip, updated_admin_id, updated_admin_ip, deleted_admin_id, deleted_admin_ip)
VALUES
    (3, '#ff0000 ', 'color_images/ff0000.png', 2, '1', '2019-08-02 07:13:09', '2019-10-15 13:22:33', 0, '', 14, '172.68.10.35', 0, '');

INSERT INTO vehicle_models
    (id, name, vehicle_brand_id, sort_order, show_status, created_at, updated_at, created_admin_id, created_admin_ip, updated_admin_id, updated_admin_ip, deleted_admin_id, deleted_admin_ip)
VALUES
    (2, 'Ace', 1, 0, '1', '2019-10-16 13:18:28', '2019-10-16 13:18:28', 0, '127.0.0.1', 0, '', 0, '');

INSERT INTO vehicle_brands
    (id, name, sort_order, show_status, created_at, updated_at, created_admin_id, created_admin_ip, updated_admin_id, updated_admin_ip, deleted_admin_id, deleted_admin_ip)
VALUES
    (1, 'AC', 0, '1', '2019-10-16 13:18:28', '2019-10-16 13:18:28', 0, '127.0.0.1', 0, '', 0, '');

INSERT INTO vehicle_colors_multilang
    (id, vehicle_color_id, language_id, name, show_status)
VALUES
    (44, 3, 1, 'Indigo', '1');

INSERT INTO cities
    (id, country_id, show_status)
VALUES
    (1, 12, '1'),
    (2, 13, '1');

INSERT INTO countries
    (id, sort_order, country_code, map_sdk, currency, currency_code, bid_step, b_radius_1, b_radius_2, price_format, show_status, time_coefficient, distance_coefficient, suggest_price_constant, min_offer_amount, available_in_landing)
VALUES
    (2, 4, 'ng', 'google', 'NGN', 'NGN', 50.00, 15.00, 7.00, '100', '1', 2, 3, 119, 125, '1'),
    (12, 5, 'ng', 'google', 'NGN', 'NGN', 50.00, 15.00, 7.00, '100', '1', 2, 3, 119, 125, '1'),
    (13, 6, 'le', 'google', 'SLL', 'SLL', 50.00, 15.00, 7.00, '100', '1', 2, 3, 119, 125, '1');

INSERT INTO zones
    (id, city_id, bid_step, b_radius_1, b_radius_2, show_status, time_coefficient, distance_coefficient, suggest_price_constant, min_offer_amount, fix_price, polygon)
VALUES
    (1, 1, 50.00, 15.00, 7.00, '1', 5, 7, 31, 240, 0, '{}'),
    (2, 2, 50.00, 15.00, 7.00, '1', 5, 7, 31, 240, 0, '{}'),
    (3, 1, 500.00, 15.00, 7.00, '1', 7, 9, 31, 300, 356, '{"0": [[[8.838393334752006,7.123647024403387],[9.299774182624638,7.13737993455964],[9.264304825588074,7.802052786122149],[8.914876428480444,7.892689993153404],[8.819270042579694,7.4642231962783905],[8.838393334752006,7.123647024403387]]]}');
