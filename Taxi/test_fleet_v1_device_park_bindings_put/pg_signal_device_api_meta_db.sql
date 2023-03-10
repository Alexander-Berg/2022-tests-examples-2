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
    'device1',
    'pub_key',
    'top_kek',
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
    'device2',
    'pub_key',
    'kek_lol',
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
    'device3',
    'pub_key',
    'just_kek',
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
    'device4',
    'pub_key',
    'another_kek',
    '07:f2:74:af:9b:c4',
    NULL,
    NULL,
    '313021120003B',
    '',
    '',
    '',
    '',
    NULL,
    NULL,
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z'
),
(
    5,
    NULL,
    TRUE,
    'device5',
    'pub_key',
    NULL,
    '09:f2:74:af:9b:c4',
    NULL,
    NULL,
    '414021120003B',
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
    1,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_2',
    3,
    '2020-08-01T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE
), (
    'park_2',
    4,
    '2020-08-01T17:00:00Z',
    '2020-08-18T17:00:00Z',
    TRUE
), (
    'park_1',
    3,
    '2020-08-18T17:00:00Z',
    '2020-08-18T17:00:00Z',
    FALSE 
);
