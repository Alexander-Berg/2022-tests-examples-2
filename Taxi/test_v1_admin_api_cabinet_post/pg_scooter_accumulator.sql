INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    depot_id,
    cabinet_name,
    type,
    updated_at,
    idempotency_token
) VALUES
(
    'aretl8d4gho7e6i3tvn1',
    '111',
    'cabinet_name1',
    'charge_station_without_id_receiver',
    '2019-12-17T07:38:55',
    '0000000000000001'
),
(
    'cabinet_id2',
    'grocery_id2',
    'cabinet_name2',
    'charge_station',
    '2019-12-17T07:38:56',
    '0000000000000002'
),
(
    'cabinet_id3',
    'grocery_id2',
    'cabinet_name3',
    'cabinet',
    '2019-12-17T07:38:57',
    '0000000000000003'
);

INSERT INTO scooter_accumulator.cells (
    cell_id,
    cabinet_id,
    accumulator_id,
    is_open,
    booked_by,
    updated_at
) VALUES
(
    '0',
    'cabinet_id2',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '1',
    'cabinet_id2',
    NULL,
    False,
    NULL,
    NOW()
);
