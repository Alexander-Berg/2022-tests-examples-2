INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES
    -- disp on s1 + paused + disconnected
    ('sip11',  '{disp}', 's1', True, False, True),
    ('sip12', '{disp}', 's1', True, False, True),
    ('sip13',  '{disp}', 's1', True, False, True),
    ('sip14',  '{disp}', 's1', True, True, True),
    ('sip15',  '{disp}', 's1', False, True, True),
    -- disp on s2
    ('sip21',  '{disp}', 's2', True, False, True),
    ('sip22', '{disp}', 's2', True, False, True),
    -- help has no subcluster
    ('sip31',  '{help}', '', True, False, True),
    -- clones which are prefixes, many agents for high priority
    ('sip41',  '{disp2}', 's2', True, False, True),
    ('sip42', '{disp2}', 's2', True, False, True),
    ('sip43',  '{disp2}', 's2', True, False, True),
    ('sip44',  '{disp2}', 's2', True, False, True),
    ('sip45',  '{dispdisp}', 's2', False, False, True),
    ('sip46',  '{dispdisp}', 's2', True, False, True),
    ('sip47', '{dispdisp}', 's2', True, False, True),
    ('sip48',  '{dispdisp}', 's2', True, False, True);
