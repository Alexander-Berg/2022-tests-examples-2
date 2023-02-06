INSERT INTO callcenter_stats.operator_status as operator
(agent_id, updated_at, status, status_updated_at, queues, login, sub_status_updated_at)
VALUES
       -- disp on s1
    ('a11', now(), 'connected', now(), array['disp_on_s1'], 'l11', now()),
    ('a12', now(), 'connected', now(), array['disp_on_s1'], 'l12', now()),
    ('a13', now(), 'connected', now(), array['disp_on_s1'], 'l13', now()),
       -- disp on s2
    ('a21', now(), 'disconnected', now(), array['disp_on_s2'], 'l21', now()),
    ('a22', now(), 'disconnected', now(), array['disp_on_s2'], 'l22', now()),
       -- cargo on s3
    ('a31', now(), 'disconnected', now(), array['cargo_on_s2'], 'l31', now()),
    ('a32', now(), 'disconnected', now(), array['cargo_on_s2'], 'l32', now())
