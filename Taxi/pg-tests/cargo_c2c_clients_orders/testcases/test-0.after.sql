INSERT INTO cargo_c2c.clients_orders (phone_pd_id, order_id, order_provider_id, updated_ts)
VALUES ('phone_pd_id_4',
        'order4',
        'cargo-c2c',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.clients_feedbacks (phone_pd_id, order_id, order_provider_id, updated_ts)
VALUES ('phone_pd_id_4',
        'order4',
        'cargo-c2c',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.orders (order_id, offer_id, updated_ts)
VALUES ('order4',
        'offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.offers (offer_id, created_ts, updated_ts)
VALUES ('offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz,
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.offers_v2 (offer_id, created_ts, updated_ts)
VALUES ('offer_id4',
        '2020-03-25T15:55:01.4183+03:00'::timestamptz,
        '2020-03-25T15:55:01.4183+03:00'::timestamptz);
