INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    depot_id,
    updated_at
) VALUES
(
    'cabinet_id1',
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
    'serial_number1',
    NULL,
    'cabinet_id1',
    NULL,
    95,
    NOW()
),
(
    'accum_id2',
    'serial_number2',
    NULL,
    'cabinet_id1',
    NULL,
    95,
    NOW()
);

