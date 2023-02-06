INSERT INTO eats_restapp_communications.send_event_data (
    event_id,
    event_type,
    event_mode,
    recipients,
    data
) VALUES (
    'fake_task',
    'daily-digest',
    'asap',
    '{"recipients": {"place_ids": [1, 2, 3]}}'::JSONB,
    '{"first": "some value", "second": "other value"}'::JSONB
);
