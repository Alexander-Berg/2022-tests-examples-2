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
    'IN_PROCESS',
    '2021-12-17T07:38:54',
    '2021-12-17T07:38:54'
),
(
    'booking_id2',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id2',
    'accum_id2',
    'PROCESSED',
    '2021-01-25T07:38:55',
    '2021-01-25T07:38:55'
),
(
    'booking_id3',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id3',
    'accum_id3',
    'VALIDATED',
    '2021-01-22T13:00:00+03:00',
    '2021-01-23T13:00:00+03:00'
),
(
    'booking_id4',
    'contractor_id1',
    'cabinet_id1',
    '1',
    'cell_id1',
    NULL,
    'CREATED',
    '2021-01-15T13:00:00+03:00',
    '2021-01-22T13:00:00+03:00'
);