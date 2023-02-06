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
    'e58e753c44e548ce9edaec0e0ef9c8c1',
    'pub_key_1',
    NULL,
    '07:f2:74:af:8b:b1',
    NULL,
    NULL,
    'ab1',
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
    external_video_file_id,
    photo_file_id,
    park_id,
    car_id,
    driver_profile_id,
    car_device_binding_id,
    driver_name,
    vehicle_plate_number
)
VALUES
(
    4,
    '64b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    1,
    '2020-02-25T23:57:00+00',
    '2020-02-25T23:57:00+00',
    'd58841a1f4b7816b84ccf4fcb7d886f7',
    '2020-02-25T23:57:00+00', -- event at
    'tired',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'file1', -- video_id
    'file2', -- external_video_id
    NULL, -- photo_id
    'p2',
    'carid2',
    'anonymous_driver_profile_id',
    NULL,
    NULL,
    NULL
);

INSERT INTO signal_device_api.videos (
  device_id,
  file_id,
  size_bytes,
  s3_path,
  started_at
)
VALUES
(1, 'file1', 10, NULL, current_timestamp);


INSERT INTO signal_device_api.video_chunks (
    device_id,
    file_id,
    offset_bytes,
    size_bytes,
    s3_path,
    concat_status
  )
VALUES
(
    1,
    'file1',
    0,
    5,
    'v1/e58e753c44e548ce9edaec0e0ef9c8c1/videos/partitions/file1/0_5.part',
    'not_concatenated'
),
(
    1,
    'file1',
    5,
    5,
    'v1/e58e753c44e548ce9edaec0e0ef9c8c1/videos/partitions/file1/5_5.part',
    'in_progress'
);
