INSERT INTO iiko_integration.orders
    (
        invoice_id,
        restaurant_order_id,
        yandex_uid,
        total_price,
        complement_amount,
        discount,
        version,
        payment_method_type,
        payment_method_id,
        items,
        changelog,
        id, idempotency_token, status, restaurant_id, expected_cashback_percentage,  currency)
VALUES
    (
        'invoice_01', -- invoice_id
        'restaurant_charge', -- restaurant_order_id
        '123456789',
        250,            -- total_price
        NULL,           -- complement_amount
        25,             -- discount
        2,              -- version
        'card',
        'card-123',
        --      prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
                ('01',  NULL,   'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,     NULL),
                ('02',  NULL,   'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,     NULL),
                ('03',  NULL,   'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,     NULL),
                ('04',  NULL,   'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'processing', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        '01', '01', ('PAYMENT_CONFIRMED','CLEARED','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 10, 'RUB'
    ),
    (
        'invoice_02', -- invoice_id
        'restaurant_charge', -- restaurant_order_id
        '123456789',
        250,            -- total_price
        NULL,           -- complement_amount
        25,             -- discount
        2,              -- version
        'card',
        'card-123',
        --      prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
                ('01',  NULL,   'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,     NULL),
                ('02',  NULL,   'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,     NULL),
                ('03',  NULL,   'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,     NULL),
                ('04',  NULL,   'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'processing_extra', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        '02', '02', ('PAYMENT_CONFIRMED','CLEARED','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 10, 'RUB'
    );
