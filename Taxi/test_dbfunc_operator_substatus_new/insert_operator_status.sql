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


INSERT INTO callcenter_stats.user_status
(sip_username, status, status_updated_at, sub_status, sub_status_updated_at, project, updated_seq)
VALUES
    ('agent01',  'disconnected', timestamptz('2020-06-22T09:40:00.00Z'), null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 1),
    ('agent02',  'disconnected', timestamptz('2020-06-22T09:40:00.00Z'),  'register_error', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 2),
    ('agent03',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 3),
    ('agent04',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 4),
    ('agent05',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 5),
    ('agent06',  'connected', timestamptz('2020-06-22T09:40:00.00Z'), 'waiting', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 6),
    ('agent07',  'connected', timestamptz('2020-06-22T09:40:00.00Z'), null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 7),
    ('agent08', 'paused', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 8),
    ('agent09',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 9),
    ('agent10',  'paused', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 10),
    ('agent11', 'paused', timestamptz('2020-06-22T09:40:00.00Z'), 'p1', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 11),
    ('agent12',  'paused', timestamptz('2020-06-22T09:40:00.00Z'),  'p2', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 12),
    ('agent13',  'paused', timestamptz('2020-06-22T09:40:00.00Z'),  'p2', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 13),
    ('agent14', 'paused', timestamptz('2020-06-22T09:40:00.00Z'),  'break', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 14),
    ('agent15',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 15),
    -- postcall procesing
    ('agent21', 'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 16),
    ('agent22','connected', timestamptz('2020-06-22T09:40:00.00Z'),  'postcall', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 17),
    ('agent23', 'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 18),
    ('agent24','connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 19),
    ('agent25',  'connected', timestamptz('2020-06-22T09:40:00.00Z'), null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 20);


INSERT INTO callcenter_stats.user_queues
(sip_username, updated_at, metaqueues, updated_seq)
VALUES
    ('agent01', now(), DEFAULT, 1),
    ('agent02', now(),array['queue1'], 2),
    ('agent03', now(),  array['queue1','queue2'], 3),
    ('agent04', now(),array['queue1','queue2'], 4),
    ('agent05', now(), array['queue1'], 5),
    ('agent06', now(),array['queue2'], 6),
    ('agent07', now(),  array['queue2'], 7),
    ('agent08', now(),array['queue2'], 8),
    ('agent09', now(), array['queue2'], 9),
    ('agent10', now(), array['queue3'], 10),
    ('agent11', now(), array['queue3'], 11),
    ('agent12', now(),array['queue3'], 12),
    ('agent13', now(), array['queue3'], 13),
    ('agent14', now(),array['queue3'], 14),
    ('agent15', now(), array['queue1'], 15),
    -- postcall procesing
    ('agent21', now(), array['queue4'], 16),
    ('agent22', now(), array['queue4'], 17),
    ('agent23', now(),  array['queue4'], 18),
    ('agent24', now(),  array['queue4'], 19),
    ('agent25', now(), array['queue4'], 20);


INSERT INTO callcenter_stats.tel_state
(sip_username, updated_at, is_connected, is_paused, is_valid, metaqueues, subcluster, updated_seq)
VALUES
    ('agent01', now(), False, False, True, DEFAULT, null, 1),
    ('agent02', now(),  False, False, True, DEFAULT, '1', 2),
    ('agent03', now(), True, False,True, array['queue1','queue2'],'1', 3),
    ('agent04', now(), True, False,True, array['queue1','queue2'], '1', 4),
    ('agent05', now(), True, False, True, array['queue1'],'1', 5),
    ('agent06', now(), True, False,True, array['queue2'],'1', 6),
    ('agent07', now(), True, False, True,array['queue2'],'1', 7),
    ('agent08', now(), True, True, True,array['queue2'], '1', 8),
    ('agent09', now(), True, False, True,array['queue2'],'1', 9),
    ('agent10', now(), True, True,True, array['queue3'], '1', 10),
    ('agent11', now(), True, True,True,array['queue3'], '1', 11),
    ('agent12', now(),True, True, True,array['queue3'], '1', 12),
    ('agent13', now(), True, True, True,array['queue3'],'1', 13),
    ('agent14', now(), True, True, True,array['queue3'],'1', 14),
    ('agent15', now(),  True, False,True, array['queue1'], '1', 15),
    -- postcall procesing
    ('agent21', now(),  True, False, True,array['queue4'],'1', 16),
    ('agent22', now(),  True, False,True,array['queue4'], '1', 17),
    ('agent23', now(),  True, False, True,array['queue4'],'1', 18),
    ('agent24', now(), True, False, True,array['queue4'], '1', 19),
    ('agent25', now(),  True, False,True, array['queue4'], '1', 20);

