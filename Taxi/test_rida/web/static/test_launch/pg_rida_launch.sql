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
