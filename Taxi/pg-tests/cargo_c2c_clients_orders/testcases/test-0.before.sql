INSERT INTO cargo_c2c.clients_orders (phone_pd_id, order_id, order_provider_id, updated_ts, terminated_at)
VALUES ('phone_pd_id_1',
        'order1',
        'cargo-c2c',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
       ('phone_pd_id_2',
        'order2',
        'cargo-c2c',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
        ('phone_pd_id_3',
        'order3',
        'cargo-c2c',
        '2020-02-28T15:55:01.4183+03:00'::timestamptz,
        '2020-02-28T15:55:01.4183+03:00'::timestamptz),
        ('phone_pd_id_4',
        'order4',
        'cargo-c2c',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz,
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.clients_feedbacks (phone_pd_id, order_id, order_provider_id, updated_ts)
VALUES ('phone_pd_id_1',
        'order1',
        'cargo-c2c',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
       ('phone_pd_id_2',
        'order2',
        'cargo-c2c',
        '2020-02-25T15:55:01.4183+03:00'::timestamptz),
        ('phone_pd_id_4',
        'order4',
        'cargo-c2c',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.orders (order_id, offer_id, updated_ts)
VALUES ('order1',
        'offer_id1',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
       ('order2',
        'offer_id2',
        '2020-02-25T15:55:01.4183+03:00'::timestamptz),
        ('order4',
        'offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.offers (offer_id, created_ts, updated_ts)
VALUES ('offer_id1',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
       ('offer_id2',
        '2020-02-25T15:55:01.4183+03:00'::timestamptz,
        '2020-02-25T15:55:01.4183+03:00'::timestamptz),
       ('offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz,
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.offers_v2 (offer_id, created_ts, updated_ts)
VALUES ('offer_id1',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz),
       ('offer_id2',
        '2020-02-25T15:55:01.4183+03:00'::timestamptz,
        '2020-02-25T15:55:01.4183+03:00'::timestamptz),
       ('offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz,
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

--- Feedbacks trigger workaround
UPDATE cargo_c2c.clients_orders
SET updated_ts = '2020-02-20T15:55:01.4183+03:00'::timestamptz
WHERE (phone_pd_id, order_id, order_provider_id) IN (
    ('phone_pd_id_1',
     'order1',
     'cargo-c2c'),
     ('phone_pd_id_2',
     'order2',
     'cargo-c2c')
);
UPDATE cargo_c2c.clients_orders
SET updated_ts = '2020-03-25T15:55:01.4183+03:00'::timestamptz
WHERE (phone_pd_id, order_id, order_provider_id) IN (
    ('phone_pd_id_4',
     'order4',
     'cargo-c2c')
);
