INSERT INTO callcenter_queues.talking_status
    (sip_username, updated_at, is_talking, metaqueue, subcluster, tech_postcall_until)
VALUES
    ('agent1', now(), true, 'queue', '1', null), -- disconnected
    ('agent3', now(), true, 'queue', '1', null), -- talking
    ('agent4', now(), true, 'queue', '2', now() + interval '10 second'), -- talking despite postcall_until field
    ('agent5', now() - interval '10 second', false, 'queue', '1', now() + interval '10 second'), -- postcall
    ('agent6', now(), true, 'queue', '1', null), -- talking
    ('agent7', now(), false, null, null, null), -- waiting
    ('agent8', now() - interval '10 second', false, 'queue', '1', now() + interval '10 second'), -- postcall
    ('agent15', now() - interval '2 minutes', false, 'queue', '1', now() - interval '1 minute'), -- waiting, postcall ended

    ('agent21', now() - interval '10 second', false, null, null, null), -- waiting
    ('agent22', now() - interval '10 second', true, 'queue', '4', null),  -- postcall from status
    ('agent23', now() - interval '10 second', false, null, null, now() + interval '10 second'),  -- postcall on unknown queue
    ('agent24', now() - interval '10 second', false, 'queue', '4', now() + interval '10 second'), -- postcall
    ('agent25', now() - interval '10 second', false, 'queue', '4', now() - interval '5 second'); -- waiting, postcall ended

INSERT INTO callcenter_queues.tel_state
    (sip_username, is_connected, is_paused, metaqueues, subcluster, is_valid, fetched_at)
VALUES
    ('agent1', false, false, DEFAULT, NULL, true, now()),
    ('agent2', false, false, array['queue'], '1', true, now()),
    ('agent3', true, false, array['queue'], '1', true, now()),
    ('agent4', true, false, array['queue'], '1', true, now()),
    ('agent5', true, false, array['queue'], '1', true, now()),
    ('agent6', true, false, array['queue'], '2', true, now()),
    ('agent7', true, false, array['queue'], '2', true, now()),
    ('agent8', true, true, array['queue'], '2', true, now()),
    ('agent9', true, false, array['queue'], '2', true, now()),
    ('agent10', true, true, array['queue'], '3', true, now()),
    ('agent11', true, true, array['queue'], '3', true, now()),
    ('agent12', true, true, array['queue'], '3', true, now()),
    ('agent13', true, true, array['queue'], '3', true, now()),
    ('agent14', true, true, array['queue'], '3', true, now()),
    ('agent15', true, false, array['queue'], '1', true, now()),
    -- postcall procesing
    ('agent21', true, false, array['queue'], '4', true, now()),
    ('agent22', true, false, array['queue'], '4', true, now()),
    ('agent23', true, false, array['queue'], '4', true, now()),
    ('agent24', true, false, array['queue'], '4', true, now()),
    ('agent25', true, false, array['queue'], '4', true, now());

