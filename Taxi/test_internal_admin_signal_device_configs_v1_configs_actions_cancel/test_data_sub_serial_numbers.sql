INSERT INTO signal_device_configs.patch_presets 
(
    id,
    patch_name, 
    patch
)
VALUES
(
    'id-1',
    'preset-1',
    ARRAY[
        '{
            "name": "system.json",
            "update": {
                        "preset_number": 1,
                        "pervoe_pole": true
                    }
        }'
    ]::JSONB[]
),
(
    'id-2',
    'preset-2',
    ARRAY[
       '{
            "name": "system.json",
            "update": {
                            "preset_number": 228,
                            "vtoroe_pole": true
                    }
        }'
    ]::JSONB[]
),
(
    'id-3',
    'preset-3',
    ARRAY[
       '{
            "name": "system.json",
            "update": {
                            "preset_number": 322,
                            "third_pole": true
                    }
        }'
    ]::JSONB[]
);
