/**
   at Moscow timezone we have:
   2 normal checks on 25.07
   1 discounted check on 25.07
   1 normal check on 24.07
*/
INSERT INTO fleet_drivers_scoring.checks
(
    park_id,
    check_id,
    idempotency_token,
    created_at,
    updated_at,
    license_pd_id,
    status,
    discount_type
)
VALUES
(
    'park1',
    'req_done1',
    '1',
    '2020-07-25 10:00:0.000000+00',
    '2020-07-25 10:00:0.000000+00',
    'license_pd_id1',
    'pending',
    'basic_price'
),
(
    'park1',
    'req_done2',
    '2',
    '2020-07-24 21:00:0.000000+00',
    '2020-07-24 21:00:0.000000+00',
    'license_pd_id2',
    'done',
    NULL
),
(
    'park1',
    'req_done_prev_day',
    '3',
    '2020-07-24 20:00:0.000000+00',
    '2020-07-24 20:00:0.000000+00',
    'license_pd_id3',
    'done',
    NULL
),
(
    'park1',
    'req_done_discounted',
    '4',
    '2020-07-25 10:00:0.000000+00',
    '2020-07-25 10:00:0.000000+00',
    'license_pd_id4',
    'done',
    'buy_x_get_y'
)


