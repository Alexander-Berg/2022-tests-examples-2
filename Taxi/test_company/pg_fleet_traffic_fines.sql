INSERT INTO fleet_traffic_fines.park_company (
    id,
    park_id,
    inn,
    kpp,
    title,
    is_deleted,
    is_active,
    updated_at,
    updated_by
) VALUES (
    '1',
    'PARK-ID-03',
    '1234567890_PD',
    '',
    'Some Name',
    False,
    True,
    '2021-12-31T00:00:00+00:00',
    'ADMIN'
), (
    '2',
    'PARK-ID-07',
    '444455556666_PD',
    '',
    'Some Name',
    False,
    True,
    '2021-12-31T00:00:00+00:00',
    'ADMIN'
), (
    '3',
    'PARK-ID-06',
    '444455556666_PD',
    '',
    'Some Name',
    False,
    True,
    '2021-12-31T00:00:00+00:00',
    'ADMIN'
), (
    '4',
    'PARK-ID-06',
    '001234567890_PD',
    '123123123_PD',
    'Some Name',
    False,
    True,
    '2021-12-31T00:00:00+00:00',
    'ADMIN'
), (
    '5',
    'PARK-ID-06',
    '123456789000_PD',
    '',
    'Title',
    False,
    False,
    '2021-12-31T12:00:00+00:00',
    'ADMIN'
), (
    '6',
    'PARK-ID-03',
    '0001110001_PD',
    '',
    'Some Name',
    TRUE,
    True,
    '2021-12-31T12:00:00+00:00',
    'ADMIN'
);
