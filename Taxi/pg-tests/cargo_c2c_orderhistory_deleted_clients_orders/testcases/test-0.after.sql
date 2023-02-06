INSERT INTO cargo_c2c.clients_orders (phone_pd_id, order_id, order_provider_id, updated_ts, terminated_at)
VALUES ('phone_pd_id_1',
        'order1',
        'cargo-c2c',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz);

INSERT INTO cargo_c2c.orderhistory_deleted_clients_orders (phone_pd_id, order_id, order_provider_id, created_ts)
VALUES ('phone_pd_id_1',
        'order1',
        'cargo-c2c',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz);
