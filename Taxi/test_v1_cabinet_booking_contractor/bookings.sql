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
    'contractor_id2',
    'aretl8d4gho7e6i3tvn1',
    '1',
    'cell_id1',
    'accum_id2',
    'CREATED',
    NOW(),
    NOW()
),
(
    'booking_id3',
    'contractor_id3',
    'aretl8d4gho7e6i3tvn1',
    '1',
    'cell_id1',
    'accum_id3',
    'IN_PROCESS',
    NOW(),
    NOW()
);
