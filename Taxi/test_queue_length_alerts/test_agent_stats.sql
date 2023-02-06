INSERT INTO callcenter_stats.call_status
(call_id, queue, status, queued_at)
VALUES
    ('11', 'ok_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('21', 'warn_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('22', 'warn_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('23', 'warn_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('31', 'crit_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('32', 'crit_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('33', 'crit_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('34', 'crit_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('35', 'crit_cc','queued', '2020-06-22T10:00:00.00Z'),
    ('36', 'crit_cc','queued', '2020-06-22T10:00:00.00Z');

INSERT INTO callcenter_stats.operator_talking_status
(agent_id, updated_at, is_talking, queue, postcall_until)
VALUES
    ('agent1', now(), true, 'warn_cc', null),
    ('agent3', now(), true, 'warn_cc', null),
    ('agent4', now(), true, 'crit_cc', null),
    ('agent5', now() - interval '10 second', false, 'warn_cc', null), -- can be postcall
    ('agent6', now(), true, 'warn_cc', null),
    ('agent7', now(), false, null, null),
    ('agent8', now() - interval '10 second', false, 'warn_cc', null), -- can be postcall
    ('agent15', now() - interval '2 minutes', false, 'warn_cc', null);

INSERT INTO callcenter_stats.operator_status
(agent_id, updated_at, status, status_updated_at, queues, sub_status_updated_at)
VALUES
    ('agent1', now(), 'disconnected', now(), DEFAULT, now()),
    ('agent2', now(), 'disconnected', now(), array['warn_cc'], now()),
    ('agent3', now(), 'connected', now(), array['warn_cc','crit_cc'], now()),
    ('agent4', now(), 'connected', now(), array['warn_cc','crit_cc'], now()),
    ('agent5', now(), 'connected', now(), array['warn_cc'], now()),
    ('agent6', now(), 'connected', now(), array['crit_cc'], now()),
    ('agent7', now(), 'connected', now(), array['crit_cc'], now()),
    ('agent8', now(), 'paused', now(), array['crit_cc'], now()),
    ('agent9', now(), 'connected', now(), array['crit_cc'], now()),
    ('agent15', now(), 'connected', now(), array['warn_cc'], now());



INSERT INTO callcenter_stats.user_status
(sip_username,  status, status_updated_at, sub_status_updated_at, project, updated_seq)
VALUES
    ('agent1', 'disconnected', now(),  now(), 'disp', 1),
    ('agent2', 'disconnected', now(), now(), 'disp', 2),
    ('agent3', 'connected', now(),  now(), 'disp', 3),
    ('agent4', 'connected', now(),  now(), 'disp', 4),
    ('agent5', 'connected', now(),  now(), 'disp', 5),
    ('agent6','connected', now(),  now(), 'disp', 6),
    ('agent7', 'connected', now(),  now(), 'disp', 7),
    ('agent8',  'paused', now(), now(), 'disp', 8),
    ('agent9', 'connected', now(), now(), 'disp', 9),
    ('agent15',  'connected', now(),  now(), 'disp', 10);

INSERT INTO callcenter_stats.user_queues
(sip_username, updated_at, metaqueues, updated_seq)
VALUES
    ('agent1', now(), DEFAULT, 1),
    ('agent2', now(), array['warn'], 2),
    ('agent3',  now(), array['warn','crit'], 3),
    ('agent4',  now(), array['warn','crit'], 4),
    ('agent5',  now(), array['warn'], 5),
    ('agent6', now(), array['crit'], 6),
    ('agent7',  now(), array['crit'], 7),
    ('agent8', now(), array['crit'], 8),
    ('agent9',  now(), array['crit'], 9),
    ('agent15',  now(), array['warn'], 10);

INSERT INTO callcenter_stats.tel_state
(sip_username, updated_at, is_connected, is_paused, is_valid, metaqueues, subcluster, updated_seq )
VALUES
    ('agent1', now(), False, False, True, DEFAULT, NULL,  1),
    ('agent2', now(),False, False,True, DEFAULT,  NULL, 2),
    ('agent3', now(), True, False,True, array['warn','crit'], 'cc',  3),
    ('agent4', now(), True, False, True, array['warn','crit'], 'cc',  4),
    ('agent5', now(), True, False,True,array['warn'], 'cc', 5),
    ('agent6', now(), True, False, True, array['crit'],  'cc', 6),
    ('agent7', now(),True, False,True, array['crit'], 'cc',  7),
    ('agent8', now(), true, True, True,array['crit'], 'cc', 8),
    ('agent9', now(), True, False,True,array['crit'], 'cc',  9),
    ('agent15', now(), True, False, True,array['warn'],  'cc', 10);
