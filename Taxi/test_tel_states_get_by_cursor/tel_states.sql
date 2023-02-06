INSERT INTO
    callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid, fetched_at)
VALUES
    ('sip_1', '{test}', '1', True, True, True, '2022-06-08T11:55:24+0000'),
    ('sip_2', '{disp}', NULL,  True, True, True, '2022-06-08T11:55:24+0000'),
    ('sip_3', '{help}', '3', True, True, True, '2022-06-08T11:55:24+0000');
