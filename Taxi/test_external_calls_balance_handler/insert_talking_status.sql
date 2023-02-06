INSERT INTO callcenter_queues.talking_status
    (sip_username, is_talking, updated_at, asterisk_call_id)
VALUES
    ('sip1',  true, NOW() - INTERVAL '4 HOUR', 'id1'),
    ('sip2', false, NOW() - INTERVAL '2 HOUR', 'id1'),
    ('sip3', false, NOW() - INTERVAL '4 HOUR', 'id1'),
    ('sip4', false, NOW() - INTERVAL '2 HOUR', 'id1'),
    ('sip5', false, NOW() - INTERVAL '2 HOUR', 'id1'),
    ('sip6', false, NOW() - INTERVAL '2 HOUR', 'id1');

INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES
    ('sip1',  '{ru_taxi_disp, disp2}', '1', True, True, True),
    ('sip2', '{ru_taxi_disp}', '1', True, True, True),
    ('sip3',  '{ru_taxi_disp, help}', '1', True, False, True),
    ('sip4',  '{ru_taxi_disp}', '1', True, False, True),
    ('sip5',  '{ru_taxi_disp}', '1', False, False, True),
    ('sip6', '{ru_taxi_disp, disp}', '1', True, False, True);
