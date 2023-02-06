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
    NULL,
    'scooter_id',
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
    'cabinet_id1',
    Null,
    True,
    'booking_id1',
    NOW()
),
(
    'cell_id2',
    'cabinet_id1',
    'accum_id2',
    False,
    'booking_id2',
    NOW()
);

INSERT INTO scooter_accumulator.bookings (
    booking_id,
    contractor_id,
    cabinet_id,
    cells_count,
    cell_id,
    accumulator_id,
    booking_status,
    created_at,
    updated_at
) VALUES
(
    'booking_id2',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id2',
    NULL,
    'PROCESSED',
    NOW(),
    NOW()
),
(
    'booking_id1',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id1',
    NULL,
    'IN_PROCESS',
    NOW(),
    NOW()
);