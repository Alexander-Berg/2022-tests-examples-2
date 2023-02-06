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
    ARRAY['sleep', 'distraction', 'some_fake'],
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
   
