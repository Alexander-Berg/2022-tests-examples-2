INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    depot_id,
    updated_at
) VALUES
(
    'cabinet_id1',
    'depot_id1',
    NOW()
),
(
    'cabinet_id2',
    'depot_id1',
    NOW()
);

INSERT INTO scooter_accumulator.accumulators (
    accumulator_id,
    serial_number,
    contractor_id,
    cabinet_id,
    scooter_id,
    charge,
    updated_at
) VALUES
(
    'accum_id1',
    'accum_serial_num1',
    'contractor_id1',
    NULL,
    NULL,
    95,
    NOW()
),
(
    'accum_id2',
    'accum_serial_num2',
    NULL,
    NULL,
    'scooter_id1',
    20,
    NOW()
),
(
    'accum_id3',
    'accum_serial_num3',
    NULL,
    'cabinet_id1',
    NULL,
    100,
    NOW()
);
