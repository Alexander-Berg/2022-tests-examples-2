INSERT INTO scooter_accumulator.cabinets (
    cabinet_id,
    depot_id,
    type,
    updated_at
) VALUES
(
    'cabinet_id1',
    'depot_id1',
    'charge_station_without_id_receiver',
    NOW()
),
(
    'cabinet_id2',
    'depot_id1',
    'charge_station',
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
    'fake_id1',
    'fake_serial1',
    NULL,
    NULL,
    NULL,
    95,
    NOW()
),
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
    100,
    NOW()
);

INSERT INTO scooter_accumulator.cells (
    cell_id,
    cabinet_id,
    accumulator_id,
    is_open,
    booked_by,
    error_code,
    updated_at
) VALUES
(
    'cell_id3',
    'cabinet_id1',
    NULL,
    True,
    'booking_id1',
    'ok',
    NOW()
),
(
    'cell_id2',
    'cabinet_id1',
    NULL,
    False,
    'booking_id2',
    'ok',
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
    'booking_id1',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id3',
    NULL,
    'IN_PROCESS',
    NOW(),
    NOW()
),
(
    'booking_id2',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id2',
    NULL,
    'CREATED',
    NOW(),
    NOW()
);
