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
(1, 'no_chunks', 10, NULL, current_timestamp),
(1, 'incomplete_single', 10, NULL, current_timestamp),
(1, 'incomplete_multi', 10, NULL, current_timestamp),
(1, 'concatenated_with_parts', 10, 'v1/abc123/concatenated_with_parts', current_timestamp),
(1, 'concatenated_no_parts', 10, 'v1/abc123/concatenated_no_parts', current_timestamp);

INSERT INTO signal_device_api.video_chunks (
  device_id,
  file_id,
  offset_bytes,
  size_bytes,
  s3_path
)
VALUES
(1, 'incomplete_single', 0, 1, 'v1/abc123/videos/partitions/incomplete_single/0_1.part'),
(1, 'incomplete_multi', 0, 3, 'v1/abc123/videos/partitions/incomplete_multi/0_3.part'),
(1, 'incomplete_multi', 3, 3, 'v1/abc123/videos/partitions/incomplete_multi/3_3.part'),
(1, 'concatenated_with_parts', 0, 5, 'v1/abc123/videos/partitions/concatenated_with_parts/0_5.part'),
(1, 'concatenated_with_parts', 5, 5, 'v1/abc123/videos/partitions/concatenated_with_parts/5_5.part');
