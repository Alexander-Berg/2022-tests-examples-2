INSERT INTO callcenter_stats.operator_talking_status as operator
    (agent_id, updated_at, is_talking, queue, postcall_until)
VALUES
    ('agent1', now(), true, 'queue1', null), -- disconnected
    ('agent3', now(), true, 'queue1', null), -- talking
    ('agent4', now(), true, 'queue2', now() + interval '10 second'), -- talking despite postcall_until field
    ('agent5', now() - interval '10 second', false, 'queue1', now() + interval '10 second'), -- postcall
    ('agent6', now(), true, 'queue1', null), -- talking
    ('agent7', now(), false, null, null), -- waiting
    ('agent8', now() - interval '10 second', false, 'queue1', now() + interval '10 second'), -- postcall
    ('agent15', now() - interval '2 minutes', false, 'queue1', now() - interval '1 minute'), -- waiting, postcall ended

    ('agent21', now() - interval '10 second', false, null, null), -- waiting
    ('agent22', now() - interval '10 second', true, 'queue4', null),  -- postcall from status
    ('agent23', now() - interval '10 second', false, null, now() + interval '10 second'),  -- postcall on unknown queue
    ('agent24', now() - interval '10 second', false, 'queue4', now() + interval '10 second'), -- postcall
    ('agent25', now() - interval '10 second', false, 'queue4', now() - interval '5 second'); -- waiting, postcall ended

INSERT INTO callcenter_stats.operator_status as operator
    (agent_id, updated_at, status, status_updated_at, queues, sub_status, sub_status_updated_at)
VALUES
    ('agent1', now(), 'disconnected', now(), DEFAULT, null, now()),
    ('agent2', now(), 'disconnected', now(), array['queue1'], null, now()),
    ('agent3', now(), 'connected', now(), array['queue1','queue2'], null, now()),
    ('agent4', now(), 'connected', now(), array['queue1','queue2'], null, now()),
    ('agent5', now(), 'connected', now(), array['queue1'], null, now()),
    ('agent6', now(), 'connected', now(), array['queue2'], 'waiting', now()),
    ('agent7', now(), 'connected', now(), array['queue2'], null, now()),
    ('agent8', now(), 'paused', now(), array['queue2'], null, now()),
    ('agent9', now(), 'connected', now(), array['queue2'], null, now()),
    ('agent10', now(), 'paused', now(), array['queue3'], null, now()),
    ('agent11', now(), 'paused', now(), array['queue3'], 'p1', now()),
    ('agent12', now(), 'paused', now(), array['queue3'], 'p2', now()),
    ('agent13', now(), 'paused', now(), array['queue3'], 'p2', now()),
    ('agent14', now(), 'paused', now(), array['queue3'], 'break', now()),
    ('agent15', now(), 'connected', now(), array['queue1'], null, now()),
    -- postcall procesing
    ('agent21', now(), 'connected', now(), array['queue4'], null, now()),
    ('agent22', now(), 'connected', now(), array['queue4'], 'postcall', now()),
    ('agent23', now(), 'connected', now(), array['queue4'], null, now()),
    ('agent24', now(), 'connected', now(), array['queue4'], null, now()),
    ('agent25', now(), 'connected', now(), array['queue4'], null, now());
