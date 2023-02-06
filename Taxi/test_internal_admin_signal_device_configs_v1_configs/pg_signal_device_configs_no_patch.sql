INSERT INTO signal_device_configs.patches (patch) 
VALUES 
(
    '{"distraction": {"enabled": false}}'::JSONB 
);

INSERT INTO signal_device_configs.device_patches (
    park_id,
    serial_number,
    canonized_software_version,
    config_name,
    updated_at,
    idempotency_token,
    patch_id
)
VALUES
(
    'p1',
    '',
    '',
    'default.json',
    '2019-09-12T00:00:00+03:00',
    'some_idempotency_token4',
    1
);
