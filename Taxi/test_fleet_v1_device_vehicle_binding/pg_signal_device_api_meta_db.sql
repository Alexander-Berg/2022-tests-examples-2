INSERT INTO signal_device_api.devices
(
    id,
    name,
    is_alive,
    public_id,
    public_key,
    imei,
    mac_wlan0,
    mac_eth0,
    mac_usb_modem,
    serial_number,
    hardware_version,
    bluetooth_password,
    wifi_password,
    user_password,
    total_ram_bytes,
    comment,
    partner_id,
    created_at,
    updated_at
)
VALUES
(
    1,
    NULL,
    TRUE,
    'device_never_bound',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b1',
    NULL,
    NULL,
    '212021120001F',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
), (
    2,
    NULL,
    TRUE,
    'device_bound',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b2',
    NULL,
    NULL,
    '212021120002D',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
), (
    3,
    NULL,
    TRUE,
    'device_bound_to_previous_park_vehicle',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b3',
    NULL,
    NULL,
    '212021120003B',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
), (
    4,
    NULL,
    TRUE,
    'device_active_in_2',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b4',
    NULL,
    NULL,
    '2120211200049',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
), (
    5,
    NULL,
    TRUE,
    'device_active_in_2_used_to_be_in_1',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b5',
    NULL,
    NULL,
    '2120211200057',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
), (
    6,
    NULL,
    TRUE,
    'device_unbound',
    'pub_key',
    'imei',
    '07:f2:74:af:8b:b6',
    NULL,
    NULL,
    '2120211200058',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
);

INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,
    created_at,
    updated_at,
    is_active
) VALUES (
    'park_1',
    1, -- device_never_bound
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_1',
    2, -- device_bound
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_2',
    3, -- device_bound_to_previous_park_vehicle
    '2020-08-01T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_1',
    3, -- device_bound_to_previous_park_vehicle
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_2',
    4, -- device_active_in_2
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_1',
    5, -- device_active_in_2_used_to_be_in_1
    '2020-08-01T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_2',
    5, -- device_active_in_2_used_to_be_in_1
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_1',
    6, -- device_unbound
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
),
-- All rows below are just duplicates of binded devices. Just checking that they will not be used
(
    'park_1',
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE 
), (
    'park_1',
    2,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_1',
    3,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE 
), (
    'park_2',
    4,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_2',
    5,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_1',
    6,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
);

INSERT INTO signal_device_api.car_device_bindings (
    id,
    park_id,
    car_id,
    device_id,
    created_at,
    detached_at,
    updated_at
) VALUES (
    '200_bound',
    'park_1',
    'car_1',
    2, -- device_bound
    '2020-08-18T18:00:00Z',
    NULL,
    '2020-08-18T18:00:00Z'
), (
    '200_bound_to_old',
    'park_2',
    'car_2',
    3, -- device_bound_to_previous_park_vehicle
    '2020-08-01T18:00:00Z',
    NULL,
    '2020-08-01T18:00:00Z'
), (
    '200_active_in_other',
    'park_2',
    'car_3',
    5, -- device_active_in_2_used_to_be_in_1
    '2020-08-18T18:00:00Z',
    NULL,
    '2020-08-18T18:00:00Z'
), (
    '200_unbound',
    'park_1',
    'car_4',
    6, -- device_unbound
    '2020-07-18T18:00:00Z',
    '2020-07-29T18:00:00Z',
    '2020-07-29T18:00:00Z'
);

INSERT INTO signal_device_api.events
(
    id,
    public_event_id,
    device_id,
    created_at,
    updated_at,
    event_id,
    event_at,
    event_type,
    gnss_latitude,
    gnss_longitude,
    gnss_speed_kmph,
    gnss_accuracy_m,
    gnss_direction_deg,
    extra,
    video_file_id,
    photo_file_id,
    park_id,
    car_id,
    driver_profile_id,
    car_device_binding_id,
    driver_name,
    vehicle_plate_number,
    resolution
)
VALUES
(
    1,
    '3f5a516f-29ff-4ebe-93eb-465bf0124e85',
    1,
    '2020-02-27T13:00:00+00',
    '2020-02-27T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076a',
    '2020-02-27T12:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'park_1',
    NULL,
    'd1',
    '1',
    'Иванов Петр',
    'K444AB55',
    'wrong_driver'
),
(
    2,
    '3f5a516f-29ff-4ebe-93eb-465bf0124e86',
    1,
    '2020-02-27T13:00:00+00',
    '2020-02-27T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076b',
    '2020-02-27T13:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'park_1',
    'car_0',
    'd1',
    '1',
    'Иванов Петр',
    'О122КХ777',
    'wrong_driver'
),
(
    3,
    '3f5a516f-29ff-4ebe-93eb-465bf0124e87',
    6,
    '2020-02-27T13:00:00+00',
    '2020-02-27T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076c',
    '2020-02-27T13:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'park_1',
    NULL,
    'd1',
    '1',
    'Иванов Петр',
    'K444AB55',
    'wrong_driver'
),
(
    4,
    '3f5a516f-29ff-4ebe-93eb-465bf0124e88',
    6,
    '2020-07-20T18:00:00+00',
    '2020-07-20T18:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076d',
    '2020-07-20T18:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'park_1',
    'car_4',
    'd1',
    '1',
    'Иванов Петр',
    'О228КХ777',
    'wrong_driver'
),
(
    5,
    '3f5a516f-29ff-4ebe-93eb-465bf0124e89',
    6,
    '2020-07-30T13:00:00+00',
    '2020-07-30T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076e',
    '2020-07-30T13:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'park_1',
    NULL,
    'd1',
    '1',
    'Иванов Петр',
    'K444AB55',
    'wrong_driver'
);
