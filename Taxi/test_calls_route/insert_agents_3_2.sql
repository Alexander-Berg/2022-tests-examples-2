INSERT INTO callcenter_stats.operator_status as operator
(agent_id, updated_at, status, status_updated_at, queues, login, sub_status_updated_at)
VALUES
       -- disp on s1 + paused + disconnected
    ('a11', now(), 'connected', now(), array['disp_on_s1'], 'l11', now()),
    ('a12', now(), 'connected', now(), array['disp_on_s1'], 'l12', now()),
    ('a13', now(), 'connected', now(), array['disp_on_s1'], 'l13', now()),
    ('a14', now(), 'paused', now(), array['disp_on_s1'], 'l14', now()),
    ('a15', now(), 'disconnected', now(), array['disp_on_s1'], 'l15', now()),
       -- disp on s2
    ('a21', now(), 'connected', now(), array['disp_on_s2'], 'l21', now()),
    ('a22', now(), 'connected', now(), array['disp_on_s2'], 'l22', now()),
       -- help has no subcluster
    ('a31', now(), 'connected', now(), array['help'], 'l31', now()),
       -- clones which are prefixes, many agents for high priority
    ('a41', now(), 'connected', now(), array['disp2_on_s2'], 'l41', now()),
    ('a42', now(), 'connected', now(), array['disp2_on_s2'], 'l42', now()),
    ('a43', now(), 'connected', now(), array['disp2_on_s2'], 'l43', now()),
    ('a44', now(), 'connected', now(), array['disp2_on_s2'], 'l44', now()),
    ('a45', now(), 'connected', now(), array['dispdisp_on_s2'], 'l45', now()),
    ('a46', now(), 'connected', now(), array['dispdisp_on_s2'], 'l46', now()),
    ('a47', now(), 'connected', now(), array['dispdisp_on_s2'], 'l47', now()),
    ('a48', now(), 'connected', now(), array['dispdisp_on_s2'], 'l48', now());

