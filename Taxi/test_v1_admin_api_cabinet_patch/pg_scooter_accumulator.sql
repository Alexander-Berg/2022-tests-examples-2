INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    cabinet_name,
    depot_id,
    type
) VALUES
(
    'cabinet_id1',
    'cabinet_name1',
    'depot_id1',
    'cabinet'
),
(
    'cabinet_id2',
    'cabinet_name2',
    'depot_id1',
    'charge_station'
),
(
    'cabinet_id3',
    'cabinet_name3',
    'depot_id1',
    'cabinet'
),
(
    'cabinet_id4',
    'cabinet_name4',
    'depot_id1',
    'cabinet'
);

INSERT INTO scooter_accumulator.accumulators (
    accumulator_id,
    serial_number,
    contractor_id,
    cabinet_id,
    scooter_id,
    charge,
    updated_at,
    created_at
) VALUES
(
    'accum_id222',
    'serial_number222',
    NULL,
    'cabinet_id3',
    NULL,
    90,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54'
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
    '1',
    'cabinet_id1',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '1',
    'cabinet_id3',
    'accum_id222',
    False,
    NULL,
    NOW()
),
(
    '2',
    'cabinet_id3',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '3',
    'cabinet_id3',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '4',
    'cabinet_id3',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '2021',
    'cabinet_id4',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '2022',
    'cabinet_id4',
    NULL,
    False,
    NULL,
    NOW()
),
(
    '2023',
    'cabinet_id4',
    NULL,
    False,
    NULL,
    NOW()
);
