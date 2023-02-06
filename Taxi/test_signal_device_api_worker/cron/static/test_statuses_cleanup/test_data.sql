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

INSERT INTO signal_device_api.status_history
(
    id,
    device_id,
    software_version,
    status_at,
    updated_at
)
VALUES
(
    'xxx',
    1,
    'xxx',
    NOW(),
    NOW()
),
(
    'yyy',
    1,
    'xxx',
    NOW() - INTERVAL '1 HOUR',
    NOW() - INTERVAL '1 HOUR'
),
(
    'zzz',
    1,
    'xxx',
    NOW() - INTERVAL '70 HOUR',
    NOW() - INTERVAL '70 HOUR'
);
