INSERT INTO signal_device_api.declared_devices (
    id,
    serial_number,
    aes_key,
    imei,
    mac_wlan0,
    mac_bluetooth,
    created_at,
    updated_at
) VALUES (
    1,
    '1234567890ABC',
    'RkFFRTRDQTNDMzBFRTE4MXmpS5A4SPr0kC5606701TZZb3I8u3uke007bZqetpw7laDnSfj34GaGywWyuFr7FkbPmuIUwAAVo1u9zteHMmM983SD8ygwSu0AlEpdSpDk', -- encrypted key 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
    '123456789012345',
    '38:fe:38:8e:84:e0',
    'e6:32:23:fc:23:9f',
    '2019-12-13T18:01:00+03:00',
    '2019-12-13T18:01:00+03:00'
);
