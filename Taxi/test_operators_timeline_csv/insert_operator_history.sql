INSERT INTO
    callcenter_stats.operator_history
    (agent_id, login, status, created_at, queues, sub_status)
VALUES
                                -- 05:00 -> 05:10
('11', 'l11', 'disconnected', '2020-01-01T04:00:00Z', array['disp_on_','support_on_'], NULL),
('12', 'l12', 'disconnected', '2020-01-01T05:05:00Z', array['disp_on_','support_on_'], NULL),
('13', 'l13', 'disconnected', '2020-01-01T06:00:00Z', array['disp_on_','support_on_'], NULL),

('21', 'l21', 'connected', '2020-01-01T04:00:00Z', default, NULL),
('222', 'l22', 'connected', '2020-01-01T05:00:00Z', array['disp_on_1'], NULL),
('23', 'l23', 'connected', '2020-01-01T05:01:01Z', array['disp_on_1'], NULL),
('24', 'l24', 'connected', '2020-01-01T05:02:59Z', array['support_on_1'], NULL),
('25', 'l25', 'connected', '2020-01-01T05:05:00Z', array['support_on_1'], NULL),
('26', 'l26', 'connected', '2020-01-01T05:10:00Z', array['disp_on_1','support_on_1'], NULL),
('27', 'l27', 'connected', '2020-01-01T06:00:00Z', array['disp_on_1','support_on_1'], NULL),

('31', 'l31', 'connected', '2020-01-01T04:00:00Z', array['support_on_1'], NULL),
('31', 'l31', 'disconnected', '2020-01-01T04:10:00Z', array['support_on_'], NULL),

('32', 'l32', 'connected', '2020-01-01T04:00:00Z', array['support_on_1'], NULL),
('32', 'l32', 'disconnected', '2020-01-01T05:05:00Z', array['support_on_'], NULL),

('33', 'l33', 'connected', '2020-01-01T05:00:00Z', array['support_on_1'], NULL),
('33', 'l33', 'disconnected', '2020-01-01T05:05:00Z', array['support_on_'], NULL),

('34', 'l34', 'connected', '2020-01-01T05:03:00Z', array['support_on_1'], NULL),
('34', 'l34', 'disconnected', '2020-01-01T05:04:00Z', array['support_on_'], NULL),

('35', 'l35', 'connected', '2020-01-01T05:04:00Z', array['support_on_1'], NULL),
('35', 'l35', 'disconnected', '2020-01-01T05:10:00Z', array['support_on_'], NULL),

('36', 'l36', 'connected', '2020-01-01T05:04:00Z', array['support_on_1'], NULL),
('36', 'l36', 'disconnected', '2020-01-01T05:15:00Z', array['support_on_'], NULL),

('37', 'l37', 'connected', '2020-01-01T05:10:00Z', array['support_on_1'], NULL),
('37', 'l37', 'disconnected', '2020-01-01T05:15:00Z', array['support_on_'], NULL),

('41', 'l41', 'connected', '2020-01-01T04:00:00Z', array['support_on_1','support_on_1'], NULL),
('41', 'l41', 'connected', '2020-01-01T05:05:00Z', array['support_on_1','support_on_1'], NULL),

('52', 'l52', 'connected',      '2020-01-01T05:00:00Z', array['disp_on_1','support_on_1'], NULL),
('52', 'l52', 'paused',         '2020-01-01T05:01:01Z', array['disp_on_1','support_on_1'], NULL),
('52', 'l52', 'connected',      '2020-01-01T05:01:59Z', array['disp_on_1','support_on_1'], NULL),
('52', 'l52', 'paused',         '2020-01-01T05:03:59Z', array['disp_on_1','support_on_1'], NULL),
('52', 'l52', 'disconnected',   '2020-01-01T05:04:01Z', array['disp_on_','support_on_'], NULL),

('53', 'l53', 'connected',      '2020-01-01T05:00:00Z', array['support_on_1'], NULL),
('53', 'l53', 'paused',         '2020-01-01T05:00:59Z', array['support_on_1'], 'break'),
('53', 'l53', 'paused',         '2020-01-01T05:01:59Z', array['support_on_1'], 'dinner'),
('53', 'l53', 'disconnected',   '2020-01-01T05:02:59Z', array['support_on_1'], 'register_error'),
('53', 'l53', 'disconnected',   '2020-01-01T05:03:01Z', array['support_on_'], NULL);
