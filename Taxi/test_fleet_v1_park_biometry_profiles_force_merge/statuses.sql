INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,  
    created_at, 
    updated_at, 
    is_active,
    group_id
)
VALUES
(
    'p1',
    1,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
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
    software_version,
    uptime_ms,
    sim_iccid,
    sim_phone_number,
    sim_imsi,
    status_at,
    created_at,
    updated_at,
    driver_detected
)
VALUES
(
    1,
    36,
    107374182,
    1073741824,
    107374183,
    1073741835,
    10737418,
    73.3242,
    54.9885,
    NULL,
    NULL,
    '2.31',
    90555,
    '89310410106543789301',
    '+7 (913) 617-82-58',
    '502130123456789',
    '2020-01-23T15:44:02',
    '2019-09-04T08:18:54',
    '2020-01-23T15:44:30',
    'anonymous_pr1'
);

INSERT INTO signal_device_api.status_history(device_id, software_version, status_at, updated_at, driver_detected) VALUES
(
    1,
    '2.31',
    '2021-01-02T00:06:00+03:00',
    '2021-01-02T00:06:00+03:00',
    'anonymous_pr1'
),
(
    1,
    '2.31',
    '2021-01-02T00:08:00+03:00',
    '2021-01-02T00:08:00+03:00',
    'anonymous_pr1'
),
(
    1,
    '2.31',
    '2021-01-02T00:08:00+03:00',
    '2021-01-02T00:08:00+03:00',
    'anonymous_pr2'
);


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
    'anonymous_pr1'
);