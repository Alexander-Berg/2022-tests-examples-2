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
    2,
    NULL,
    TRUE,
    'd58e753c44e548ce9edaec0e0ef9c8c1',
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
),
(
    3,
    NULL,
    TRUE,
    'd58e753c44e548ce9edaec0e0ef9c8c3',
    'pub_key_3',
    '990000862471853',
    '07:f2:74:af:8b:b3',
    NULL,
    NULL,
    'AB3',
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
    '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
    2,
    '2020-02-27T13:02:00+00',
    '2020-02-27T13:02:00+00',
    '7faebfa97bfafe293023a41a49250ak3',
    '2020-02-27T11:02:00+00',
    'driver_lost',
    54.94550000,
    73.36822151,
    89.437895,
    NULL,
    NULL,
    '',
    NULL,
    NULL,
    'p1',
    'c1',
    'd1',
    '1',
    '???????????? ????????',
    'K444AB55',
    NULL
),
(
    2,
    '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    2,
    '2020-02-27T13:00:00+00',
    '2020-02-27T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076f',
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
    'p1',
    'c1',
    'd2',
    '1',
    '???????????? ????????',
    'K123KK777',
    NULL
),
(
    3,
    '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
    3,
    '2020-02-27T13:00:00+00',
    '2020-02-27T13:00:00+00',
    '0ef0466e6e1331b3a7d35c585983076g',
    '2020-02-27T12:00:00+00',
    'sleep',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    'video.mp4',
    'photo.jpg',
    'p1',
    'c1',
    NULL,
    '1',
    NULL,
    NULL,
    NULL
),
(
    4,
    '10f5a516f-29ff-4ebe-93eb-465bf0124e85',
    3,
    '2020-02-25T13:00:00+00',
    '2020-02-25T13:00:00+00',
    'xxf0466e6e1331b3a7d35c585983076g',
    '2020-02-25T12:00:00+00',
    'distraction',
    54.99250000,
    73.36861111,
    34.437895,
    0.61340,
    245.895,
    '1',
    NULL,
    NULL,
    'p1',
    'c1',
    NULL,
    '1',
    NULL,
    NULL,
    'delete'
),
(
    5,
    '5f5a516f-228f-4ebe-93eb-465bf0124e85',
    2,
    '2020-02-27T13:02:00+00',
    '2020-02-27T13:02:00+00',
    '7faebfa97bfafe293023a41a49250ak4',
    '2020-02-27T11:02:00+00',
    'type_not_in_whitelist',
    54.94550000,
    73.36822151,
    89.437895,
    NULL,
    NULL,
    '',
    NULL,
    NULL,
    'p1',
    'c1',
    'd1',
    '1',
    '???????????? ????????',
    'K444AB55',
    NULL
);

INSERT INTO signal_device_api.videos
(
    device_id,
    file_id,
    size_bytes,
    started_at,
    s3_path,
    created_at,
    updated_at
)
VALUES
(
    3,
    'video.mp4',
    300,
    current_timestamp,
    'some/s3/path.mp4',
    current_timestamp,
    current_timestamp
);
