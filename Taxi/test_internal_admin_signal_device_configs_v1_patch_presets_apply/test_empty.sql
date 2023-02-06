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

