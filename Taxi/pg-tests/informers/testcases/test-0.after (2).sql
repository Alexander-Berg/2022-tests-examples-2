INSERT INTO orders_tracking.informers
    (order_id, informer_type, created, compensation_type, situation_code, cancel_reason, raw_compensation_info)
VALUES
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, 'long_courier_search'::orders_tracking.informer_type, '2020-12-31T18:00:00.0000+03:00'::timestamptz, NULL, NULL, NULL, NULL),
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, 'long_courier_search'::orders_tracking.informer_type, '2021-01-01T01:00:00.0000+03:00'::timestamptz, NULL, NULL, NULL, NULL),
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, 'long_courier_search'::orders_tracking.informer_type, '2021-01-01T05:00:00.0000+03:00'::timestamptz, NULL, NULL, NULL, NULL),
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, 'long_courier_search'::orders_tracking.informer_type, '2021-01-01T11:00:00.0000+03:00'::timestamptz, NULL, NULL, NULL, NULL);
