INSERT INTO fleet_traffic_fines.cars_sync (
    license_plate,
    registration_certificate,
    sync_status
) VALUES (
    'CARNUMBER01',
    'CARSTS01',
    'active'
), (
    'CARNUMBER02',
    'CARSTS02',
    'adding'
), (
    'CARNUMBER03',
    'CARSTS03',
    'removing'
);

INSERT INTO fleet_traffic_fines.park_cars (
    car_id,
    park_id,
    license_plate,
    registration_certificate,
    updated_at,
    is_rental
) VALUES (
    'CAR_ID_01',
    'PARK-ID-01',
    'CARNUMBER01',
    'CARSTS01',
    '2022-01-01T12:00:00.000000+03:00',
    True
), (
    'CAR_ID_02',
    'PARK-ID-02',
    'CARNUMBER02',
    'CARSTS02',
    '2022-01-01T12:00:00.000000+03:00',
    True
), (
    'CAR_ID_02',
    'PARK-ID-01',
    'CARNUMBER02',
    'CARSTS02',
    '2022-01-01T12:00:00.000000+03:00',
    True
), (
    'CAR_ID_03',
    'PARK-ID-03',
    'CARNUMBER01',
    'CARSTS01',
    '2022-01-01T12:00:00.000000+03:00',
    False
);

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
    1,
    'PARK-ID-04',
    '1234567890_PD',
    '',
    'Title',
    False,
    True,
    '2021-11-01T12:00:00.000000+03:00',
    'ADMIN'
), (
    2,
    'PARK-ID-01',
    '1234567890_PD',
    '',
    'Title',
    False,
    True,
    '2021-11-01T12:00:00.000000+03:00',
    'ADMIN'
), (
    3,
    'PARK-ID-05',
    '0123456789_PD',
    '123123_PD',
    'Title',
    False,
    True,
    '2021-11-01T12:00:00.000000+03:00',
    'ADMIN'
);
