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
    False,
    'booking_id1',
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
    'cell_id1',
    'accum_id1',
    'CREATED',
    NOW(),
    NOW()
);
