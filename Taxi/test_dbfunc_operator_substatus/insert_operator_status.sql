INSERT INTO callcenter_stats.operator_talking_status as operator
    (agent_id, updated_at, is_talking, queue, postcall_until)
VALUES
    ('agent01', timestamptz('2020-06-22T10:00:00.00Z'), true, 'queue1_on_1', null), -- disconnected
    ('agent03', timestamptz('2020-06-22T10:00:00.00Z'), true, 'queue1_on_1', null), -- talking
    ('agent04', timestamptz('2020-06-22T10:00:00.00Z'), true, 'queue2_on_1', timestamptz('2020-06-22T10:00:00.00Z') + interval '10 second'), -- talking despite postcall_until field
    ('agent05', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, 'queue1_on_1', timestamptz('2020-06-22T10:00:00.00Z') + interval '10 second'), -- postcall
    ('agent06', timestamptz('2020-06-22T10:00:00.00Z'), true, 'queue1_on_1', null), -- talking
    ('agent07', timestamptz('2020-06-22T10:00:00.00Z'), false, null, null), -- waiting
    ('agent08', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, 'queue1_on_1', timestamptz('2020-06-22T10:00:00.00Z') + interval '10 second'), -- postcall
    ('agent15', timestamptz('2020-06-22T10:00:00.00Z') - interval '2 minutes', false, 'queue1_on_1', timestamptz('2020-06-22T10:00:00.00Z') - interval '1 minute'), -- waiting, postcall ended

    ('agent21', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, null, null), -- waiting
    ('agent22', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', true, 'queue4_on_1', null),  -- postcall from status
    ('agent23', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, null, timestamptz('2020-06-22T10:00:00.00Z') + interval '10 second'),  -- postcall on unknown queue
    ('agent24', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, 'queue4_on_1', timestamptz('2020-06-22T10:00:00.00Z') + interval '10 second'), -- postcall
    ('agent25', timestamptz('2020-06-22T10:00:00.00Z') - interval '10 second', false, 'queue4_on_1', timestamptz('2020-06-22T10:00:00.00Z') - interval '5 second'); -- waiting, postcall ended


INSERT INTO callcenter_stats.operator_status as operator
    (agent_id, updated_at, status, status_updated_at, queues, sub_status, sub_status_updated_at)
VALUES
    ('agent01', now(), 'disconnected', timestamptz('2020-06-22T09:40:00.00Z'), DEFAULT, null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent02', now(), 'disconnected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1'], 'register_error', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent03', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1','queue2_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent04', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1','queue2_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent05', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent06', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue2_on_1'], 'waiting', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent07', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue2_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent08', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue2_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent09', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue2_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent10', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue3_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent11', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue3_on_1'], 'p1', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent12', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue3_on_1'], 'p2', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent13', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue3_on_1'], 'p2', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent14', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue3_on_1'], 'break', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent15', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    -- postcall procesing
    ('agent21', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue4_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent22', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue4_on_1'], 'postcall', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent23', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue4_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent24', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue4_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent25', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue4_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z'));

