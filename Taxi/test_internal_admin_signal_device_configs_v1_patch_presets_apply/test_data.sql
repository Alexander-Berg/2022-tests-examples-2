INSERT INTO signal_device_configs.patch_presets 
(
    id,
    patch_name, 
    patch
)
VALUES
(
    'id-mqtt',
    'Настройки mqtt',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                        "mqtt": 
                            {
                                "enabled": true
                            },
                        "fallback": "some_conf"
                      }
        }'
    ]::JSONB[]
),
(
    'id-1',
    'Настройки mqtt2',
    ARRAY[
        '{
            "name": "system.json",
            "update": {"mqtt": "NULL"}
        }'
    ]::JSONB[]
),
(
    'id-2',
    'Настройки system-1',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                        "distraction": 
                            {
                                "enabled": true
                            }
                       }
        }'
    ]::JSONB[]
),
(
    'id-3',
    'Настройки system-2',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                        "new_field":
                            {
                                "enabled": true
                            }
                       }
        }'
    ]::JSONB[]
),
(  
    'id-4',
    'Выключить фиксацию отвлечения',
    ARRAY[
        '{
            "name": "system.json",
            "update": {"stream_meta": false}
        }',
        '{
            "name": "default.json",
            "update": {"distraction": {"enabled": false}}
        }'
    ]::JSONB[]
);

INSERT INTO signal_device_configs.patches (patch) 
VALUES 
(
    '{
        "distraction": true
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false}
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL"
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "some_old_event": {"enabled": false}
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL"
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "some_old_event": {"enabled": false}
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL",
        "some_old_event": {"enabled": false}
    }'::JSONB 
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL",
        "some_old_event": {"enabled": false}
    }'::JSONB 
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
    '',
    '',
    '',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    1
),
(
    'p1',
    '',
    '',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    2
),
(
    '',
    'serial1',
    '',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    3
),
(
    '',
    '',
    '0000000000.0000000000.0000000000-0000000001',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    4
),
(
    'p1',
    'serial1',
    '',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    5
),
(
    'p1',
    '',
    '0000000000.0000000000.0000000000-0000000001',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    6
),
(
    '',
    'serial1',
    '0000000000.0000000000.0000000000-0000000001',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    7
),
(
    'p1',
    'serial1',
    '0000000000.0000000000.0000000000-0000000001',
    'system.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    8
);

INSERT INTO signal_device_configs.actions (id, patch_preset_id)
VALUES ('f37a495c-d7a2-488f-b7da-93dd2fa3bdcd', 1)
