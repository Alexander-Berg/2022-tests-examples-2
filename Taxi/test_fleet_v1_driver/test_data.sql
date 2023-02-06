INSERT INTO signal_device_api.events
(
    id,
    device_id,
    created_at,
    updated_at,
    event_id,
    public_event_id,
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
    driver_profile_id
)
VALUES
(
    1,
    1,
    '2020-02-27T13:00:00',
    '2020-02-27T13:00:00',
    '0ef0466e6e1331b3a7d35c585983076a',
    '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    '2020-02-27T12:00:00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    'video_id_ok',
    NULL,
    'p1',
    'd1'
),
(
    2,
    1,
    '2020-02-28T13:02:00',
    '2020-02-28T13:02:00',
    '7faebfa97bfafe293023a41a49250ac3',
    '44b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    '2020-02-27T12:02:00',
    'fart',
    54.94550000,
    73.36822151,
    89.437895,
    NULL,
    NULL,
    '',
    'video_id_not_uploaded_yet',
    'photo_id_not_uploaded_yet',
    'p1',
    'd1'
),
(
    3,
    2,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e94c0875963785801eed76c4322b394',
    '54b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    '2020-02-26T23:55:00',
    'sleep',
    54.99550072,
    72.94622044,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'photo_id_ok',
    NULL,
    NULL
);

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
    'd1',
    'pub_key_1',
    '990000862471854',
    '07:f2:74:af:8b:b1',
    NULL,
    NULL,
    'AB1',
    '1.01',
    '0gp72Eh6hA5qjcgpohV3HnWgMGOgezJBMrCzF/Rp/YqQt8U0l4tutD09xWZmlWai',
    'qUOqr6n0bzKUcxsVVzywQKJNTmxIqDNfW9usyTB5wdg=',
    'rkmTiizJVfTN/YwkOH3A26y5j36X0Y8jZmorCEXmJgufrQq0FeP5PPAzwU403Buv',
    NULL,
    NULL,
    1,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54'
),
(
    2,
    NULL,
    TRUE,
    'd2',
    'pub_key_2',
    '990000862471852',
    '07:f2:74:af:8b:b2',
    NULL,
    NULL,
    'AB2',
    '1.01',
    '0gp72Eh6hA5qjcgpohV3HnWgMGOgezJBMrCzF/Rp/YqQt8U0l4tutD09xWZmlWai',
    'qUOqr6n0bzKUcxsVVzywQKJNTmxIqDNfW9usyTB5wdg=',
    'rkmTiizJVfTN/YwkOH3A26y5j36X0Y8jZmorCEXmJgufrQq0FeP5PPAzwU403Buv',
    NULL,
    NULL,
    1,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54'
);

INSERT INTO signal_device_api.status_history
(
  device_id,
  software_version,
  status_at,
  updated_at,
  states_id,
  driver_detected
)
VALUES
(
    1,
    '2.31',
    '2021-01-02T00:06:00+03:00',
    '2021-01-02T00:06:00+03:00',
    NULL,
    NULL
),
(
    2,
    '2.31',
    '2021-03-04T00:06:00+03:00',
    '2021-03-04T00:06:00+03:00',
    NULL,
    'd1'
),
(
    2,
    '2.31',
    '2021-03-04T20:51:00+03:00',
    '2021-03-04T20:51:00+03:00',
    NULL,
    'd1'
),
(
    1,
    '2.31',
    NOW() - INTERVAL '5 MINUTES',
    NOW() - INTERVAL '5 MINUTES',
    NULL,
    'd2'
);

INSERT INTO signal_device_api.statuses
(
    id,
    cpu_temperature,
    disk_bytes_free_space,
    disk_bytes_total_space,
    root_bytes_free_space,
    root_bytes_total_space,
    ram_bytes_free_space,
    gps_position_lat,
    gps_position_lon,
    gnss_latitude,
    gnss_longitude,
    gnss_speed_kmph,
    gnss_accuracy_m,
    gnss_direction_deg,
    software_version,
    uptime_ms,
    sim_iccid,
    sim_phone_number,
    sim_imsi,
    status_at,
    created_at,
    updated_at,
    position_updated_at,
    states_id,
    driver_detected
)
VALUES
(
    2,
    36,
    107374182,
    1073741824,
    107374183,
    1073741835,
    10737418,
    73.3242,
    54.9885,
    53.3242,
    34.9885,
    10,
    3,
    100,
    '2.31',
    90555,
    '89310410106543789301',
    '+7 (913) 617-82-58',
    '502130123456789',
    '2021-03-04T00:05:00+03:00',
    '2021-09-04 T08:18:54 +03:00',
    '2021-08-11 15:00:00 +03:00',
    NULL,
    NULL,
    'd1'
);

INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,
    created_at,
    updated_at,
    is_active
) 
VALUES
(
    'p1',
    2,
    '2021-03-04T00:04:00+03:00',
    '2021-03-04T00:08:00+03:00',
    FALSE
);