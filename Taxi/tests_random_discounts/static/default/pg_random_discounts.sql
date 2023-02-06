INSERT INTO random_discounts.random_discounts
(random_discount_id, yandex_uid, device_id, completed_at, discount_series, discount, discount_limit, discount_ttl_mins, coupon_code)
VALUES 
  (0, 'active_id', 'active_dev', '2020-01-09 08:00:00 UTC', 'coolseries', 30, 150, 1440, 'couponcode'),
  (1, 'inactive_id', 'inactive_dev', '2020-01-09 10:00:00 UTC', 'coolseries', 30, 150, 1440, NULL),
  (2, 'time_uid', 'time_device_id', '2020-01-09 10:10:01 UTC', 'coolseries', NULL, 150, 1440, NULL)
;
