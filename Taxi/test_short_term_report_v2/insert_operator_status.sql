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
    ('agent02', now(), 'disconnected', now(), array['queue1_on_1'], null, now()),
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

INSERT INTO callcenter_stats.user_status
(sip_username, status, status_updated_at, sub_status, sub_status_updated_at, project, updated_seq)
VALUES
    ('agent01',  'disconnected', now(), null,now(), 'disp', 1),
    ('agent02',  'disconnected', now(),  'register_error',now(), 'disp', 2),
    ('agent03',  'connected', now(),  null,now(), 'disp', 3),
    ('agent04',  'connected', now(),  null,now(), 'disp', 4),
    ('agent05',  'connected', now(),  null,now(), 'disp', 5),
    ('agent06',  'connected', now(), 'waiting',now(), 'disp', 6),
    ('agent07',  'connected', now(), null,now(), 'disp', 7),
    ('agent08', 'paused', now(),  null,now(), 'disp', 8),
    ('agent09',  'connected', now(),  null,now(), 'disp', 9),
    ('agent10',  'paused', now(),  null,now(), 'disp', 10),
    ('agent11', 'paused', now(), 'p1',now(), 'disp', 11),
    ('agent12',  'paused', now(),  'p2',now(), 'disp', 12),
    ('agent13',  'paused', now(),  'p2',now(), 'disp', 13),
    ('agent14', 'paused', now(),  'break',now(), 'disp', 14),
    ('agent15',  'connected', now(),  null,now(), 'disp', 15),
    -- postcall procesing
    ('agent21', 'connected', now(),  null,now(), 'disp', 16),
    ('agent22','connected', now(),  'postcall',now(), 'disp', 17),
    ('agent23', 'connected', now(),  null,now(), 'disp', 18),
    ('agent24','connected', now(),  null,now(), 'disp', 19),
    ('agent25',  'connected', now(), null,now(), 'disp', 20);


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
    ('agent01', now(), False, False, True,DEFAULT, null, 1),
    ('agent02', now(),  False, False, True,DEFAULT, '1', 2),
    ('agent03', now(), True, False, True,array['queue1','queue2'],'1', 3),
    ('agent04', now(), True, False, True,array['queue1','queue2'], '1', 4),
    ('agent05', now(), True, False, True,array['queue1'],'1', 5),
    ('agent06', now(), True, False, True,array['queue2'],'1', 6),
    ('agent07', now(), True, False, True,array['queue2'],'1', 7),
    ('agent08', now(), True, True, True,array['queue2'], '1', 8),
    ('agent09', now(), True, False, True,array['queue2'],'1', 9),
    ('agent10', now(), True, True, True,array['queue3'], '1', 10),
    ('agent11', now(), True, True,True,array['queue3'], '1', 11),
    ('agent12', now(),True, True, True,array['queue3'], '1', 12),
    ('agent13', now(), True, True, True,array['queue3'],'1', 13),
    ('agent14', now(), True, True, True,array['queue3'],'1', 14),
    ('agent15', now(),  True, False, True,array['queue1'], '1', 15),
    -- postcall procesing
    ('agent21', now(),  True, False, True,array['queue4'],'1', 16),
    ('agent22', now(),  True, False,True,array['queue4'], '1', 17),
    ('agent23', now(),  True, False, True,array['queue4'],'1', 18),
    ('agent24', now(), True, False,True, array['queue4'], '1', 19),
    ('agent25', now(),  True, False,True, array['queue4'], '1', 20);
