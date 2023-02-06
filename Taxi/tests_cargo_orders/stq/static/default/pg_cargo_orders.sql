INSERT INTO cargo_orders.orders
    (commit_state, order_id, waybill_ref, provider_order_id, provider_user_id, use_cargo_pricing)
VALUES
    ('done', '9db1622e-582d-4091-b6fc-4cb2ffdc12c0', 'waybill-ref', 'taxi-order', 'taxi_user_id_1', true);

INSERT INTO cargo_orders.orders_performers (
    order_id,
    order_alias_id,
    phone_pd_id,
    name,
    driver_id,
    park_id,
    park_clid,
    park_name,
    park_org_name,
    car_id,
    car_number,
    car_model,
    lookup_version,
    tariff_class
)
VALUES (
    '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'order_alias_id',
    'phone_pd_id',
    'Kostya',
    'driver_id1',
    'park_id1',
    'park_clid1',
    'some_park_name',
    'some_park_org_name',
    'car_id1',
    'some_car_number',
    'some_car_model',
    1,
    'cargo'
);

INSERT INTO cargo_orders.orders
    (commit_state, order_id, waybill_ref, provider_order_id, provider_user_id, use_cargo_pricing)
VALUES
    ('done', '7771622e-4091-582d-b6fc-4cb2ffdc12c0', 'waybill-ref-no-performer', 'taxi-order2', 'taxi_user_id_1', true);
