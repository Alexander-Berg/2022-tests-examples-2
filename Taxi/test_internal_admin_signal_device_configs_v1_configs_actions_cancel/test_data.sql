INSERT INTO signal_device_configs.patch_presets 
(
    id,
    patch_name, 
    patch
)
VALUES
(
    'id-0',
    'distraction',
    ARRAY[
        '{
            "name": "system.json",
            "update": {"distraction": true}
        }'
    ]::JSONB[]
),
(
    'id-1',
    'stream_meta',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                "stream_meta": {
                    "enabled": false
                }
            }
        }'
    ]::JSONB[]
),
(
    'id-2',
    'mqtt',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                "mqtt": {
                    "enabled": false,
                    "timeout": 0.5
                },
                "fallback": "NULL"
            }
        }'
    ]::JSONB[]
),
(  
    'id-3',
    'some_old_event',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                "some_old_event": {
                    "enabled": false
                }
            }
        }'
    ]::JSONB[]
);
-- action1 = 0598a7e7-dd77-4fa2-813a-1e13ab3afda7
-- action2 = 51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7
-- action3 = 1bf10f86-1913-48b9-b4ab-ee35ccdde491
-- action4 = 6fe8bba9-3e72-41e2-adf4-59e382a5a967
INSERT INTO signal_device_configs.patches (patch, action_history) 
VALUES 
(
    '{
        "distraction": true
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7']::TEXT[]
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false}
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7']::TEXT[]
),
(
    '{
        "distraction": true,
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL"
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '1bf10f86-1913-48b9-b4ab-ee35ccdde491']::TEXT[]
),
(
    '{
        "distraction": true,
        "some_old_event": {"enabled": false}
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '6fe8bba9-3e72-41e2-adf4-59e382a5a967']::TEXT[]
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL"
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7', '1bf10f86-1913-48b9-b4ab-ee35ccdde491']::TEXT[]
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "some_old_event": {"enabled": false}
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7', '6fe8bba9-3e72-41e2-adf4-59e382a5a967']::TEXT[]
),
(
    '{
        "distraction": true,
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL",
        "some_old_event": {"enabled": false}
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '1bf10f86-1913-48b9-b4ab-ee35ccdde491', '6fe8bba9-3e72-41e2-adf4-59e382a5a967']::TEXT[]
),
(
    '{
        "distraction": true,
        "stream_meta": {"enabled": false},
        "mqtt": {"enabled": false, "timeout": 0.5}, "fallback": "NULL",
        "some_old_event": {"enabled": false}
    }'::JSONB,
    ARRAY['0598a7e7-dd77-4fa2-813a-1e13ab3afda7', '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7', '1bf10f86-1913-48b9-b4ab-ee35ccdde491', '6fe8bba9-3e72-41e2-adf4-59e382a5a967']::TEXT[]
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

INSERT INTO signal_device_configs.actions 
(
    id, 
    patch_preset_id, 
    park_id, 
    serial_numbers, 
    software_version
)
VALUES 
(
    '0598a7e7-dd77-4fa2-813a-1e13ab3afda7', 
    'id-0',
    '',
    ARRAY['']::TEXT[],
    ''
),
(
    '51a1f7f0-00ef-41d3-aba2-d9a648ccf2d7', 
    'id-1',
    'p1',
    ARRAY['']::TEXT[],
    ''
),
(
    '1bf10f86-1913-48b9-b4ab-ee35ccdde491', 
    'id-2',
    '',
    ARRAY['serial1']::TEXT[],
    ''
),
(
    '6fe8bba9-3e72-41e2-adf4-59e382a5a967', 
    'id-3',
    '',
    ARRAY['']::TEXT[],
    '0000000000.0000000000.0000000000-0000000001'
);
