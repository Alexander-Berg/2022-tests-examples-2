INSERT INTO  cache.offers (
    order_id,
    last_access_time,
    status,
    yt_request
) VALUES (
    'order_old',
    '2020-01-10 18:23:11.5857+03',
    'READY',
    ('order_old', 'anylink', 'econom', '2020-01-01 05:23:11.5857+03', false, 'timezone', '123')
),
(
    'order_new',
    '2020-08-08 18:23:11.5857+03',
    'READY',
    ('order_new', 'anylink', 'econom', '2020-08-01 05:23:11.5857+03', false, 'timezone', '')
),
(
    'order_may',
    '2020-05-10 18:23:11.5857+03',
    'READY',
    ('order_may', 'anylink', 'econom', '2020-05-01 05:23:11.5857+03', false, 'timezone', '')
);
