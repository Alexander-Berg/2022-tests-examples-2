INSERT INTO callcenter_stats.operator_talking_status as operator
    (agent_id, updated_at, is_talking, queue, postcall_until)
VALUES
    ('agent01', timestamptz('2020-06-22T10:00:00.10Z'), true, 'queue1_on_1', null), -- talking
    ('agent02', timestamptz('2020-06-22T10:00:00.20Z'), true, 'queue2_on_2', null), -- talking
    ('agent03', timestamptz('2020-06-22T10:00:00.30Z'), false, 'queue2_on_2', timestamptz('2020-06-22T10:00:00.00Z') + interval '10 seconds'); -- postcall


INSERT INTO callcenter_stats.operator_status as operator
    (agent_id, updated_at, status, status_updated_at, queues, sub_status, sub_status_updated_at)
VALUES
    ('agent01', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_1'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent02', now(), 'paused', timestamptz('2020-06-22T09:40:00.00Z'), array['queue2_on_2'], 'break', timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent03', now(), 'connected', timestamptz('2020-06-22T09:40:00.00Z'), array['queue1_on_2','queue2_on_2'], null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent04', now(), 'disconnected', timestamptz('2020-06-22T09:40:00.00Z'), DEFAULT, null, timestamptz('2020-06-22T09:50:00.00Z')),
    ('agent10', now(), 'disconnected', timestamptz('2020-06-22T09:55:00.00Z'), DEFAULT, null, timestamptz('2020-06-22T09:55:00.00Z')),
    ('agent11', now(), 'disconnected', timestamptz('2020-06-22T09:56:00.00Z'), DEFAULT, 'register_error', timestamptz('2020-06-22T09:56:00.00Z'));



INSERT INTO callcenter_stats.user_status
(sip_username,  status, status_updated_at, sub_status, sub_status_updated_at, project, updated_seq)
VALUES
    ('agent01',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 1),
    ('agent02',  'paused', timestamptz('2020-06-22T09:40:00.00Z'), 'break', timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 2),
    ('agent03',  'connected', timestamptz('2020-06-22T09:40:00.00Z'),  null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 3),
    ('agent04',  'disconnected', timestamptz('2020-06-22T09:40:00.00Z'), null, timestamptz('2020-06-22T09:50:00.00Z'), 'disp', 4),
    ('agent10',  'disconnected', timestamptz('2020-06-22T09:55:00.00Z'), null, timestamptz('2020-06-22T09:55:00.00Z'), 'disp', 5),
    ('agent11', 'disconnected', timestamptz('2020-06-22T09:56:00.00Z'), 'register_error', timestamptz('2020-06-22T09:56:00.00Z'), 'disp', 6);



INSERT INTO callcenter_stats.user_queues
(sip_username, updated_at, metaqueues, updated_seq)
VALUES
    ('agent01', now(), array['queue1'],1),
    ('agent02', now(), array['queue2'], 2),
    ('agent03', now(), array['queue1','queue2'], 3),
    ('agent04', now(),DEFAULT,4),
    ('agent10', now(), DEFAULT, 5),
    ('agent11', now(), DEFAULT, 6);



INSERT INTO callcenter_stats.tel_state
(sip_username, updated_at, is_connected, is_paused, is_valid, metaqueues, subcluster, updated_seq)
VALUES
    ('agent01', now(), True, False, True, array['queue1'], '1', 1),
    ('agent02', now(), True, True,True, array['queue2'], '2', 2),
    ('agent03', now(),True, False, True,array['queue1','queue2'], '2', 3),
    ('agent04', now(), False, False, True,DEFAULT, null, 4),
    ('agent10', now(), False, False, True, DEFAULT, null, 5),
    ('agent11', now(), False, False, True, DEFAULT, null, 6);
