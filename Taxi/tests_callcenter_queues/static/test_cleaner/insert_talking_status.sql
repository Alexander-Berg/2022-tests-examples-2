INSERT INTO callcenter_queues.talking_status
    (sip_username, is_talking, updated_at, asterisk_call_id)
VALUES
    ('dt4',  true, NOW() - INTERVAL '4 HOUR', 'id1'),
    ('dt2', true, NOW() - INTERVAL '2 HOUR', 'id1'),
    ('ht4', true, NOW() - INTERVAL '4 HOUR', 'id1'),
    ('ht2', true, NOW() - INTERVAL '2 HOUR', 'id1');

INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES
    ('dt4',  '{disp}', '1', True, True, True),
    ('dt2', '{disp}', '1', True, True, True),
    ('ht4',  '{help}', '1', True, True, True),
    ('ht2', '{help}', '1', True, True, True);
