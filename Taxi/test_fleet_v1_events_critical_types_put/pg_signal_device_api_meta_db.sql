INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,  
    created_at, 
    updated_at, 
    is_active,
    group_id
)
VALUES
(
    'p1',
    1,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
),
(
    'p2',
    2,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
);

INSERT INTO signal_device_api.park_critical_event_types
(
    park_id,
    critical_event_types,
    created_at,
    updated_at
)
VALUES
(
    'p1',
    ARRAY['sleep', 'distraction'],
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
   
