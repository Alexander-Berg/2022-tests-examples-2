INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, launch_id)
VALUES ('push', 1, 'start', NOW(), (NOW() - INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'), 'a0eebc999c0b4ef8bb6d6bb9bd380a11');


INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, launch_id)
VALUES ('reserve_push', 1, 'delivered', NOW(), (NOW() - INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'),
        'a0eebc999c0b4ef8bb6d6bb9bd380a11');

INSERT INTO steps (step, scenario_id, waiting_event, start_at, deadline, status, lock_deadline, launch_id)
VALUES ('sms', 1, 'delivered', NOW(), (NOW() - INTERVAL '1 hour'), 'waiting', (NOW() + INTERVAL '1 hour'),
        'a0eebc999c0b4ef8bb6d6bb9bd380a11');
