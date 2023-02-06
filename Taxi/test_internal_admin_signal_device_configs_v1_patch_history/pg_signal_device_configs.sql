INSERT INTO signal_device_configs.patches (id, patch, action_history) 
VALUES
(
    4,
    '{
        "stream_meta": true, 
        "notify_manager_config": "/etc/signalq/notify_manager-alisa.json"
    }'::JSONB,
    '{"action-1","action-id33","action-2"}'::TEXT[]
),
(
    1,
    '{ "test": {"test": 3} }'::JSONB,
    NULL
);

INSERT INTO signal_device_configs.patch_presets 
(
    id,
    patch_name, 
    patch
)
VALUES
(
    'id-1',
    'Включить стрим мету',
    ARRAY[
        '{
            "name": "system.json",
            "update": {"stream_meta": true}
        }'
    ]::JSONB[]
),
(
    'id-2',
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
),
(
    'id-3',
    'Озвучка Алисы',
    ARRAY[
        '{
            "name": "system.json",
            "update": {"notify_manager_config": "/etc/signalq/notify_manager-alisa.json"}
        }'
    ]::JSONB[]
);


INSERT INTO signal_device_configs.actions (
    id,
    patch_preset_id,
    park_id,
    serial_numbers,
    software_version,
    created_at
)
VALUES
(
    'action-1',
    'id-3',
    '',
    ARRAY['serial1'],
    '',
    '2019-12-11T00:00:00+03:00'
),
(   
    'action-id33',
    'id-2',
    '',
    ARRAY['serial1'],
    '',
    '2019-12-12T00:00:00+03:00'
),
(
    'action-2',
    'id-1',
    '',
    ARRAY['serial1'],
    '',
    '2019-12-12T00:00:00+03:00'
);
