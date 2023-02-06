INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    depot_id,
    type,
    updated_at
) VALUES
(
    'aretl8d4gho7e6i3tvn1',
    '111',
    'charge_station_without_id_receiver',
    NOW()
),
(
    'cabinet_id2',
    'grocery_id2',
    'charge_station',
    NOW()
),
(
    'cabinet_id3',
    'grocery_id2',
    'cabinet',
    NOW()
),
(
    'cabinet_id4',
    'grocery_id2',
    'cabinet',
    NOW()
),
(
    'cabinet_id5',
    'grocery_id2',
    'cabinet',
    NOW()
),
(
    'cabinet_id6',
    'grocery_id2',
    'charge_station',
    NOW()
),
(
    'cabinet_id7',
    'grocery_id2',
    'cabinet',
    NOW()
);

INSERT INTO scooter_accumulator.accumulators (
    idempotency_token,
    accumulator_id,
    serial_number,
    contractor_id,
    cabinet_id,
    scooter_id,
    charge,
    updated_at
) VALUES
(
    '0000000000000001',
    'accum_id1',
    'serial_number1',
    NULL,
    'cabinet_id2',
    NULL,
    95,
    NOW()
),
(
    '0000000000000002',
    'accum_id2',
    'serial_number2',
    NULL,
    'aretl8d4gho7e6i3tvn1',
    NULL,
    100,
    NOW()
),
(
    '0000000000000003',
    'accum_id3',
    'serial_number3',
    NULL,
    'aretl8d4gho7e6i3tvn1',
    NULL,
    50,
    NOW()
),
(
    '0000000000000004',
    'accum_id4',
    'serial_number4',
    NULL,
    'cabinet_id2',
    NULL,
    90,
    NOW()
),
(
    '0000000000000005',
    'accum_id5',
    'serial_number5',
    NULL,
    'cabinet_id4',
    NULL,
    90,
    NOW()
),
(
    '0000000000000007',
    'accum_id6',
    'serial_number6',
    NULL,
    NULL,
    'scooter_id1',
    90,
    NOW()
),
(
    '0000000000000008',
    'accum_id7',
    'serial_number7',
    NULL,
    'cabinet_id7',
    NULL,
    90,
    NOW()
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
    'cell_id1',
    'cabinet_id2',
    'accum_id1',
    False,
    NULL,
    NOW()
),
(
    'cell_id2',
    'aretl8d4gho7e6i3tvn1',
    'accum_id2',
    False,
    NULL,
    NOW()
),
(
    'cell_id3',
    'aretl8d4gho7e6i3tvn1',
    'accum_id3',
    False,
    NULL,
    NOW()
),
(
    '1',
    'cabinet_id2',
    'accum_id4',
    False,
    NULL,
    NOW()
),
(
    'cell_id4',
    'cabinet_id2',
    NULL,
    False,
    NULL,
    NOW()
),
(
    'cell_id5',
    'cabinet_id3',
    NULL,
    False,
    NULL,
    NOW()
),
(
    'cell_id6',
    'cabinet_id3',
    NULL,
    False,
    NULL,
    NOW()
),
(
    'cell_id7',
    'cabinet_id5',
    NULL,
    False,
    NULL,
    NOW()
),
(
    'cell_id8',
    'cabinet_id6',
    NULL,
    False,
    NULL,
    NOW()
),
(
    'cell_id9',
    'cabinet_id4',
    'accum_id5',
    False,
    NULL,
    NOW()
),
(
    'cell_id10',
    'cabinet_id7',
    'accum_id7',
    False,
    NULL,
    NOW()
);