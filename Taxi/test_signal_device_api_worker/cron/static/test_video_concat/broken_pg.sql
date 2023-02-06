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

INSERT INTO signal_device_api.videos (
  device_id,
  file_id,
  size_bytes,
  s3_path,
  started_at
)
VALUES
(1, 'broken_missing_start_pg', 10, NULL, current_timestamp),
(1, 'broken_missing_middle_pg', 10, NULL, current_timestamp),
(1, 'broken_extra_pg', 10, NULL, current_timestamp);

INSERT INTO signal_device_api.video_chunks (
  device_id,
  file_id,
  offset_bytes,
  size_bytes,
  s3_path
)
VALUES
(1, 'broken_missing_start_pg', 1, 9, 'v1/abc123/videos/partitions/broken_missing_start_pg/1_9.part'),
(1, 'broken_missing_middle_pg', 0, 5, 'v1/abc123/videos/partitions/broken_missing_middle_pg/0_5.part'),
(1, 'broken_missing_middle_pg', 7, 3, 'v1/abc123/videos/partitions/broken_missing_middle_pg/7_3.part'),
(1, 'broken_extra_pg', 0, 5, 'v1/abc123/videos/partitions/broken_extra_pg/0_5.part'),
(1, 'broken_extra_pg', 5, 6, 'v1/abc123/videos/partitions/broken_extra_pg/5_6.part');
