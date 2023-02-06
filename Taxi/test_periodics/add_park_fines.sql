
INSERT INTO fleet_traffic_fines.park_fines (
    fine_uin,
    car_id,
    park_id,
    status,
    issued_at,
    was_loaded_bank_client,
    loaded_at,
    updated_at
) VALUES (
    'FINE_UIN_01',
    'CAR_ID_01',
    'PARK-ID-01',
    'issued',
    '2022-01-01T00:00:00+00:00',
    False,
    '2022-01-01T00:00:00+00:00',
    '2022-01-01T00:00:00+00:00'
), (
    'FINE_UIN_01',
    'CAR_ID_01',
    'PARK-ID-02',
    'issued',
    '2022-01-01T00:00:00+00:00',
    False,
    '2022-01-01T00:00:00+00:00',
    '2022-01-01T00:00:00+00:00'
), (
    'FINE_UIN_02',
    'CAR_ID_02',
    'PARK-ID-01',
    'issued',
    '2021-12-31T00:00:00+00:00',
    False,
    '2021-12-31T00:00:00+00:00',
    '2021-12-31T00:00:00+00:00'
), (
    'FINE_UIN_03',
    NULL,
    'PARK-ID-03',
    'paid',
    '2021-12-31T00:00:00+00:00',
    False,
    '2021-12-31T00:00:00+00:00',
    '2021-12-31T00:00:00+00:00'
);
