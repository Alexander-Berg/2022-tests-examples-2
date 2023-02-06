INSERT INTO ad_ip_lookup
    (ip_from, ip_to, country_code, country_name)
VALUES (0, 3758090239, 'NG', 'Nigeria');

INSERT INTO countries_multilang
    (country_id, language_id, name, show_status, created_at, updated_at)
VALUES 
    (12, 1, 'Nigeria', '1', '2019-10-08 11:05:43', '2019-10-08 11:05:58');

INSERT INTO offer_cancel_reasons 
    (id, user_type, reason, sort_order, show_status, created_at, updated_at)
VALUES 
    (0, 'passenger', 'mistake', 0, '1', '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (1, 'passenger', 'another', 1, '1', '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (2, 'driver', 'tired', 0, '1', '2019-10-08 11:05:58', '2019-10-08 11:05:58');

INSERT INTO offer_cancel_reasons_multilang 
    (id, offer_cancel_reasons_id, language_id, reason_name, show_status)
VALUES
    (0, 0, 1, 'mistake', '1'),
    (1, 1, 1, 'another', '1'),
    (2, 2, 1, 'tired', '1');

INSERT INTO country_has_offer_cancel_reasons
    (id, country_id, offer_cancel_reasons_id, sort_order, created_at, updated_at)
VALUES
    (0, 12, 0, 0, '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (1, 12, 1, 1, '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (2, 12, 2, 2, '2019-10-08 11:05:58', '2019-10-08 11:05:58');

INSERT INTO payment_methods
    (id, alias, sort_order, show_status, created_at, updated_at)
VALUES
    (0, 'cash', 0, '1', '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (1, 'bank_transfer', 1, '1', '2019-10-08 11:05:58', '2019-10-08 11:05:58');

INSERT INTO country_has_payment_methods
    (id, country_id, payment_methods_id, sort_order, created_at, updated_at)
VALUES
    (0, 12, 0, 0, '2019-10-08 11:05:58', '2019-10-08 11:05:58'),
    (1, 12, 1, 0, '2019-10-08 11:05:58', '2019-10-08 11:05:58');

INSERT INTO payment_methods_multilang
    (id, payment_methods_id, language_id, name, show_status)
VALUES
    (0, 0, 1, 'Cache', '1'),
    (1, 1, 1, 'Transfer', '1');

TRUNCATE TABLE countries;
INSERT INTO countries
    (id, sort_order, country_code, map_sdk, currency, currency_code, bid_step, b_radius_1, b_radius_2, price_format, show_status, time_coefficient, distance_coefficient, suggest_price_constant, min_offer_amount, available_in_landing)
VALUES
    (12, 5, 'ng', 'google', 'NGN', 'NGN', 50.00, 15.00, 7.00, '100', '1', 2, 3, 119, 125, '1');


TRUNCATE TABLE users;
INSERT INTO users
    (id, guid, first_name, last_name, msisdn, avatar, language_id, country_code)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'first_name', 'last_name', 'msisdn', 'avatar', 1, 'ng'),
    (1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 'first_name', 'last_name', 'msisdn', 'avatar', 1, 'ng'),
    (1448, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', 'first_name', 'last_name', 'msisdn', 'avatar', 1, 'ng');

TRUNCATE TABLE drivers;
INSERT INTO drivers
    (id, driver_id, guid, avg_rating, current_balance, city_id, country_id, partner_id, has_vehicle, internal_comments, reg_step, number_of_trips, driver_status, created_at, updated_at, moderation_data, sign_up_date, first_bid_created, first_order_created, is_for_testing, driver_data)
VALUES
    (582, 1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 0.00, 0.00, null, 12, null, '0', '', '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0', null),
    (583, 1448, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 5.00, 0.00, null, 12, null, '0', '', '', 0, 'new', '2019-10-08 11:05:43', '2019-10-08 11:05:58', '', null, '0', '0', '0', '{"permit_number": "AA018913"}');


INSERT INTO offers
    (id, created_at, offer_guid, user_guid, driver_guid, offer_status, point_a, point_b, initial_price)
VALUES
    (1, '2022-02-22 11:05:58', 'offer_1', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 'COMPLETE', '', '',  100),
    (2, '2022-02-22 11:05:58', 'offer_2', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 'PASSENGER_CANCELLED', '', '',  100),
    (3, '2022-02-22 11:05:58', 'offer_2', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', '9373F48B-C6B4-4812-A2D0-XXXXXXXXXXXX', 'PASSENGER_CANCELLED', '', '',  100),
    (4, '2022-02-22 11:05:58', 'offer_3', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', null, 'PASSENGER_CANCELLED', '', '',  100);
