INSERT INTO signal_device_configs.events_fixated
(
    park_id,
    event_types,
    created_at,
    updated_at
)
VALUES
(
    'p1',
    ARRAY['tired', 'distraction', 'unusual_event_type'],
    '2019-12-12T00:00:00+03:00',
    '2019-12-12T00:00:00+03:00'
),
(
    'p2',
    ARRAY['tired', 'smoking', 'seatbelt'],
    '2019-12-12T00:00:00+03:00',
    '2019-12-12T00:00:00+03:00'
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
    'fixation of tired',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"drowsiness": {"events": {"tired": {"enabled": false}}}}
        }'
    ]::JSONB[]
), (
    'id-4',
    'fixation of seatbelt',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"seatbelt": {"events": {"seatbelt": {"enabled": false}}}}
        }'
    ]::JSONB[]
), (
    'id-5',
    'fixation of smoking',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"smoking": {"events": {"smoking": {"enabled": false}}}}
        }'
    ]::JSONB[]
), (
    'id-6',
    'fixation of distraction',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"distraction": {"events": {"distraction": {"enabled": false}}}}
        }'
    ]::JSONB[]
), (
    'id-7',
    'fixation of bad_camera_pose',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"general": {"events": {"bad_camera_pose": {"enabled": false}}}}
        }'
    ]::JSONB[]
), (
    'id-8',
    'fixation of alarm',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"general": {"events": {"alarm": {"enabled": false}}}}
        }'
    ]::JSONB[]
),
(
    'id-9',
    'Включить стрим мету, только теперь это фьючерс',
    ARRAY[
        '{
            "name": "features.json",
            "update": {"stream_meta": true}
        }'
    ]::JSONB[]
);

INSERT INTO signal_device_configs.patches (patch, action_history)
VALUES
(
    '{"distraction": {"events": {"distraction": {"enabled": false}}}}'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "xxx": 555,
        "yyy": 333
    }'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "some_field1": {
            "some_field12": "xxx"
        },
        "some_field2": 1241.4
    }'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "aaa": 111,
        "bbb": 222
    }'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "distraction": {
            "events": {
                "distraction": {
                    "enabled": false
                }
            }
        },
        "drowsiness": {
            "events": {
                "tired": {
                    "enabled": false
                }
            }
        },
        "some_old_event": {
            "enabled": false
        }
    }'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "default_v1": {"default": 3}
    }'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "general": {
            "events": {
                "bad_camera_pose": {
                    "enabled": false
                }
            }
        },
        "distraction": {
            "events": {
                "distraction": {
                    "enabled": false
                }
            }
        }
    }'::JSONB,
    ARRAY[
        '303da9a4-05eb-4ed6-88a9-07e71eb745c6',
        '29a86437-b4ca-47e1-878a-3faadc116f17'
    ]::text[]
),
(
    '{
        "distraction": {
            "events": {
                "distraction": {
                    "enabled": false
                }
            }
        },
        "seatbelt": {
            "events": {
                "seatbelt": {
                    "enabled": false
                }
            }
        }
    }'::JSONB,
    ARRAY[
        'b831a29f-e21a-4c1b-bf95-a47bfc2c074a',
        '08e783bc-b601-46c9-ab3c-72a772922ecb'
    ]::text[]
),
(
    '{"seatbelt": {"events": {"seatbelt": {"enabled": false}}}}'::JSONB,
    ARRAY[]::text[]
),
(
    '{
        "distraction": {
            "events": {
                "distraction": {
                    "enabled": false
                }
            }
        },
        "stream_meta": true
    }',
    ARRAY[
        'c73f33e4-33fd-4ba4-a758-25907008068a',
        '9914e1cc-755b-4a25-84fe-f900d3d9d8d0'
    ]::TEXT[]
),
(
    '{
        "stream_meta": true
    }',
    ARRAY[
        'c7877738-62c1-4d1b-8fba-05052320e2f9'
    ]::TEXT[]
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
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    1
),
(
    'p1',
    'BBB2TT00LL22FF',
    '',
    'system.json',
    '2019-12-12T00:00:00+03:00',
    'some_idempotency_token1',
    2
),
(
    'p1',
    '',
    '0000000000.0000000000.0000000006-0000000003',
    'other.json',
    '2019-12-12T00:00:00+03:00',
    'some_idempotency_token1',
    3
),
(
    'p1',
    'BBB2TT00LL22FF',
    '0000000000.0000000000.0000000006-0000000003',
    'system.json',
    '2019-12-11T23:59:00+03:00',
    'some_idempotency_token1',
    4
),
(
    'p2',
    '',
    '',
    'features.json',
    '2019-12-13T00:00:00+03:00',
    'some_idempotency_token1',
    5
),
(
    'p2',
    'AAA2TT00LL22FF',
    '0000000000.0000000000.0000000007-0000000003',
    'system.json',
    '2019-12-12T00:00:00+03:00',
    'some_idempotency_token1',
    4
),
(
    '',
    '',
    '',
    'default.json',
    '2019-09-12T00:00:00+03:00',
    'some_idempotency_token4',
    6
),
(
    'p7',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    7
),
(
    'p9',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    7
),
(
    'p10',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    8
),
(
    'p11',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    9
),
(
    'p12',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    10
),
(
    'p13',
    '',
    '',
    'features.json',
    '2019-12-11T00:00:00+03:00',
    'some_idempotency_token0',
    11
);

INSERT INTO signal_device_configs.actions (
    id,
    patch_preset_id,
    park_id
)
VALUES
(
    'b831a29f-e21a-4c1b-bf95-a47bfc2c074a',
    'id-4',
    'p10'
),
(
    '08e783bc-b601-46c9-ab3c-72a772922ecb',
    'id-6',
    'p10'
),
(
    '303da9a4-05eb-4ed6-88a9-07e71eb745c6',
    'id-7',
    'p7'
),
(
    '29a86437-b4ca-47e1-878a-3faadc116f17',
    'id-6',
    'p7'
),
(
    'c73f33e4-33fd-4ba4-a758-25907008068a',
    'id-9',
    'p12'
),
(
    '9914e1cc-755b-4a25-84fe-f900d3d9d8d0',
    'id-6',
    'p12'
),
(
    'c7877738-62c1-4d1b-8fba-05052320e2f9',
    'id-9',
    'p13'
)
