INSERT INTO coupons.errors_log
    (created, coupon, error_code, cart_id, yandex_uid, personal_phone_id, coupon_type)
VALUES
    ('2021-02-01T01:00:00.0000+03:00'::timestamptz, 'some_error', '6776feef-01bb-400c-ab48-840fc00e0693'::UUID, '123', NULL, NULL),
    ('2021-02-01T05:00:00.0000+03:00'::timestamptz, 'some_error', '6776feef-01bb-400c-ab48-840fc00e0694'::UUID, '123', NULL, NULL),
    ('2021-02-01T11:00:00.0000+03:00'::timestamptz, 'some_error', '6776feef-01bb-400c-ab48-840fc00e0695'::UUID, '123', NULL, NULL);
