INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES
    -- disp on s1 + paused + disconnected
    ('a',  '{disp}', 's1', True, False, True);

INSERT INTO callcenter_queues.target_status
(
    sip_username,
    status,
    project,
    updated_seq
)
VALUES
    ('a', 'connected', 'disp', 1);

INSERT INTO callcenter_queues.target_queues
(
    sip_username,
    metaqueues,
    updated_seq
)
VALUES
    ('a', '{disp}'::VARCHAR[], 1);
