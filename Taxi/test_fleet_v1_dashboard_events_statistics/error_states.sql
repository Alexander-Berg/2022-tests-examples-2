INSERT INTO signal_device_api.devices
(
  id,
  is_alive,
  public_id,
  public_key,
  mac_wlan0,
  serial_number,
  hardware_version,
  bluetooth_password,
  wifi_password,
  user_password,
  created_at,
  updated_at
)
VALUES
(
  1,
  TRUE,
  'e58e753c44e548ce9edaec0e0ef9c8c1',
  'pub_key_1',
  '07:f2:74:af:8b:b1',
  'AB1',
  '1.01',
  '0gp72Eh6hA5qjcgpohV3HnWgMGOgezJBMrCzF/Rp/YqQt8U0l4tutD09xWZmlWai',
  'qUOqr6n0bzKUcxsVVzywQKJNTmxIqDNfW9usyTB5wdg=',
  'rkmTiizJVfTN/YwkOH3A26y5j36X0Y8jZmorCEXmJgufrQq0FeP5PPAzwU403Buv',
  '2019-12-17T07:38:54',
  '2019-12-17T07:38:54'
),
(
  2,
  TRUE,
  '4306de3dfd82406d81ea3c098c80e9ba',
  'pub_key_2',
  'a5:90:c5:98:95:48',
  'AB12FE45DD',
  '1.02',
  'bk+tiOIGu8pvtW6t1Ua4A5GWt0OVW0Y+9eMYu86lp7cTDQwiME5Ls+3FA6Ey2Anc',
  '5R9B0pS+FUWoppjfv4jpyo3QnZtgvqeETTwsnjruUaM=',
  'Eyu+mWRi9K6XhyxnXiy30qagNcQwIh8cuDNXbqkTWN9NBGXjwzdI8lwljEGW3fg1',
  '2019-12-17T08:38:54',
  '2019-12-17T08:38:54'
);

INSERT INTO signal_device_api.declared_devices
(
  serial_number,
  aes_key,
  imei,
  mac_wlan0,
  mac_bluetooth,
  created_at,
  updated_at
)
VALUES
(
  'AB1',
  'RkFFRTRDQTNDMzBFRTE4MXmpS5A4SPr0kC5606701TZZb3I8u3uke007bZqetpw7laDnSfj34GaGywWyuFr7FkbPmuIUwAAVo1u9zteHMmM983SD8ygwSu0AlEpdSpDk', -- encrypted key 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
  '123456789012345',
  '38:fe:38:8e:84:e0',
  'e6:32:23:fc:23:9f',
  '2019-12-13T18:01:00+03:00',
  '2019-12-13T18:01:00+03:00'
),
(
  'AB12FE45DD',
  'QkdFRTRDQTNDMzBFRTE4MXmpS5A4SPr0kC5606701TZZb3I8u3uke007bZqetpw7laDnSfj34GaGywWyuFr7Fh5HfrooCCxNlL4c70zbixWvvMNO/L72PH43uJP1NBx2', -- encrypted key 'BGEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521993A'
  '983456789012367',
  '58:fe:38:8e:84:e1',
  'a6:32:23:fc:23:9g',
  '2019-12-13T18:01:00+03:00',
  '2019-12-13T18:01:00+03:00'
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
  1,
  NOW(),
  NOW(),
  TRUE
),
(
  'p1',
  2,
  NOW(),
  NOW(),
  TRUE
);

INSERT INTO signal_device_api.device_error_states
(
  day,
  serial_number,
  error_type,
  duration,
  is_last_state
)
VALUES
(
  '2020-02-27',
  'AB1',
  'bad_camera_pose1337',
  INTERVAL '5 MINUTE',
  TRUE
),
(
  '2020-02-27',
  'AB12FE45DD',
  'trash_frames',
  INTERVAL '12 HOUR' + INTERVAL '1 SECOND',
  FALSE
);