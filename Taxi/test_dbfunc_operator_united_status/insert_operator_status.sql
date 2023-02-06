INSERT INTO callcenter_stats.operator_talking_status as operator
    (agent_id, updated_at, is_talking, queue, postcall_until)
VALUES
    ('agent01', now(), true, 'queue1_on_1', null), -- disconnected
    ('agent03', now(), true, 'queue1_on_1', null), -- talking
    ('agent04', now(), true, 'queue2_on_1', now() + interval '10 second'), -- talking despite postcall_until field
    ('agent05', now() - interval '10 second', false, 'queue1_on_1', now() + interval '10 second'), -- postcall
    ('agent06', now(), true, 'queue1_on_1', null), -- talking
    ('agent07', now(), false, null, null), -- waiting
    ('agent08', now() - interval '10 second', false, 'queue1_on_1', now() + interval '10 second'), -- postcall
    ('agent15', now() - interval '2 minutes', false, 'queue1_on_1', now() - interval '1 minute'), -- waiting, postcall ended

    ('agent21', now() - interval '10 second', false, null, null), -- waiting
    ('agent22', now() - interval '10 second', true, 'queue4_on_1', null),  -- postcall from status
    ('agent23', now() - interval '10 second', false, null, now() + interval '10 second'),  -- postcall on unknown queue
    ('agent24', now() - interval '10 second', false, 'queue4_on_1', now() + interval '10 second'), -- postcall
    ('agent25', now() - interval '10 second', false, 'queue4_on_1', now() - interval '5 second'); -- waiting, postcall ended


INSERT INTO callcenter_stats.operator_status as operator
    (agent_id, updated_at, status, status_updated_at, queues, sub_status, sub_status_updated_at)
VALUES
    ('agent01', now(), 'disconnected', now(), DEFAULT, null, now()),
    ('agent02', now(), 'disconnected', now(), array['queue1_on_1'], 'register_error', now()),
    ('agent03', now(), 'connected', now(), array['queue1_on_1','queue2_on_1'], null, now()),
    ('agent04', now(), 'connected', now(), array['queue1_on_1','queue2_on_1'], null, now()),
    ('agent05', now(), 'connected', now(), array['queue1_on_1'], null, now()),
    ('agent06', now(), 'connected', now(), array['queue2_on_1'], 'waiting', now()),
    ('agent07', now(), 'connected', now(), array['queue2_on_1'], null, now()),
    ('agent08', now(), 'paused', now(), array['queue2_on_1'], null, now()),
    ('agent09', now(), 'connected', now(), array['queue2_on_1'], null, now()),
    ('agent10', now(), 'paused', now(), array['queue3_on_1'], null, now()),
    ('agent11', now(), 'paused', now(), array['queue3_on_1'], 'p1', now()),
    ('agent12', now(), 'paused', now(), array['queue3_on_1'], 'p2', now()),
    ('agent13', now(), 'paused', now(), array['queue3_on_1'], 'p2', now()),
    ('agent14', now(), 'paused', now(), array['queue3_on_1'], 'break', now()),
    ('agent15', now(), 'connected', now(), array['queue1_on_1'], null, now()),
    -- postcall procesing
    ('agent21', now(), 'connected', now(), array['queue4_on_1'], null, now()),
    ('agent22', now(), 'connected', now(), array['queue4_on_1'], 'postcall', now()),
    ('agent23', now(), 'connected', now(), array['queue4_on_1'], null, now()),
    ('agent24', now(), 'connected', now(), array['queue4_on_1'], null, now()),
    ('agent25', now(), 'connected', now(), array['queue4_on_1'], null, now());

