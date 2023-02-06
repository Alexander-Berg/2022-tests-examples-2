INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, waiting_event_id,
                   launch_id)
VALUES ('push', 1, 'delivered', NOW(), (NOW() + INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'), '0xFFFD',
        'a0eebc999c0b4ef8bb6d6bb9bd380a11');

INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, waiting_event_id,
                   launch_id)
VALUES ('reserve_push', 1, 'delivered', NOW(), (NOW() + INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'),
        '0xFFFE',
        'a0eebc999c0b4ef8bb6d6bb9bd380a11');

INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, waiting_event_id,
                   launch_id)
VALUES ('sms', 1, 'delivered', NOW(), (NOW() + INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'), '0xFFFF',
        'a0eebc999c0b4ef8bb6d6bb9bd380a11');
