INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES
    -- disp on s1 + paused + disconnected
    ('sip11',  '{disp}', 's1', True, False, True),
    ('sip12', '{disp}', 's1', True, False, True),
    ('sip13',  '{disp}', 's1', True, False, True),
    -- disp on s2
    ('sip21',  '{disp}', 's2', False, False, True),
    ('sip22', '{disp}', 's2', False, False, True),
    -- help has no subcluster
    ('sip31',  '{cargo}', 's2', False, False, True),
    ('sip32',  '{cargo}', 's2', False, False, True);
