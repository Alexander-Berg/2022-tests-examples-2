INSERT INTO corp_orders.tanker_orders (
    id,
    client_id,
    department_id,
    user_id,
    yandex_uid,
    personal_phone_id,
    created_at,
    updated_at,
    closed_at,
    status,
    cancellation_reason,
    payment_method,
    price_per_liter,
    preliminary_price,
    final_price,
    final_price_wo_discount,
    events_price,
    discount,
    currency,
    station_name,
    station_address,
    station_location,
    station_pump,
    fuel_type,
    fuel_name,
    liters_requested,
    liters_filled,
    liters_log
) VALUES (
    'order_id_1',
    'client_id_1',
    'department_id_1',
    'user_id_1',
    'yandex_uid_1',
    'personal_phone_id_1',
    '2021-11-30T10:30:00.123+03:00'::timestamptz,
    '2021-11-30T10:31:00.123+03:00'::timestamptz,
    '2021-11-30T10:32:00.123+03:00'::timestamptz,
    'Completed',
    NULL,
    'corp',
    '60.23',
    '849.85',
    '1426.29',
    '1447.93',
    '1426.29',
    '21.64',
    'RUB',
    'Тестировочная №1',
    'Кремлевская наб. 1',
    (37.64015961, 55.73690033),
    '3',
    'a100_premium',
    'АИ-100 Ultimate',
    '14.11',
    '24.04',
    ARRAY[
        row('2022-01-13T09:45:11.629Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:13.657Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:15.681Z', 1.34)::corp_orders.liter_log,
        row('2022-01-13T09:45:17.705Z', 2.67)::corp_orders.liter_log
    ]
),
(
    'order_id_2',
    'client_id_1',
    'department_id_1',
    'user_id_1',
    'yandex_uid_1',
    'personal_phone_id_1',
    '2021-11-30T11:30:00.123+03:00'::timestamptz,
    '2021-11-30T11:31:00.123+03:00'::timestamptz,
    NULL,
    'Fueling',
    NULL,
    'card',
    '60.23',
    '849.85',
    '1426.29',
    '1447.93',
    '1426.29',
    '21.64',
    'RUB',
    'Тестировочная №1',
    'Кремлевская наб. 1',
    (37.64015961, 55.73690033),
    '3',
    'a100_premium',
    'АИ-100 Ultimate',
    '14.11',
    '24.04',
    ARRAY[
        row('2022-01-13T09:45:11.629Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:13.657Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:15.681Z', 1.34)::corp_orders.liter_log,
        row('2022-01-13T09:45:17.705Z', 2.67)::corp_orders.liter_log
    ]
),
(
    'order_id_3',
    'client_id_1',
    'department_id_1',
    'user_id_2',
    'yandex_uid_1',
    'personal_phone_id_1',
    '2021-11-30T13:30:00.123+03:00'::timestamptz,
    '2021-11-30T13:31:00.123+03:00'::timestamptz,
    '2021-11-30T13:32:00.123+03:00'::timestamptz,
    'Completed',
    NULL,
    'corp',
    '60.23',
    '849.85',
    '1426.29',
    '1447.93',
    '1426.29',
    '21.64',
    'RUB',
    'Тестировочная №1',
    'Кремлевская наб. 1',
    (37.64015961, 55.73690033),
    '3',
    'a100_premium',
    'АИ-100 Ultimate',
    '14.11',
    '24.04',
    ARRAY[
        row('2022-01-13T09:45:11.629Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:13.657Z', NULL)::corp_orders.liter_log,
        row('2022-01-13T09:45:15.681Z', 1.34)::corp_orders.liter_log,
        row('2022-01-13T09:45:17.705Z', 2.67)::corp_orders.liter_log
    ]
);
