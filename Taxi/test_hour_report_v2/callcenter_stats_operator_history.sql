INSERT INTO
    callcenter_stats.operator_history
    (agent_id, login, status, created_at, queues, prev_status, prev_created_at, prev_queues)
VALUES
                                -- 09:00 -> 10:00
('11', 'l11', 'disconnected', '2020-06-23T05:00:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0
('12', 'l12', 'disconnected', '2020-06-23T09:30:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0
('13', 'l13', 'disconnected', '2020-06-23T11:00:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0

('21', 'l21', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),       -- > 1h, 0
('22', 'l22', 'connected', '2020-06-23T09:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),       -- > 1h, 0
('23', 'l23', 'connected', '2020-06-23T09:10:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),       -- > 50m, 0
('24', 'l24', 'connected', '2020-06-23T10:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),       -- > 0, 0
('25', 'l25', 'connected', '2020-06-23T11:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),       -- > 0, 0

('31', 'l31', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('31', 'l31', 'disconnected', '2020-06-23T06:00:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['disp_on_1','support_on_1']),     -- > 0, 0

('32', 'l32', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('32', 'l32', 'disconnected', '2020-06-23T09:10:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['disp_on_1','support_on_1']),     -- > 10m, 0

('33', 'l33', 'connected', '2020-06-23T09:00:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('33', 'l33', 'disconnected', '2020-06-23T09:50:00Z', DEFAULT, 'connected', '2020-06-23T09:00:00Z', array['disp_on_1','support_on_1']),     -- > 50m, 0

('34', 'l34', 'connected', '2020-06-23T09:10:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('34', 'l34', 'disconnected', '2020-06-23T09:50:00Z', DEFAULT, 'connected', '2020-06-23T09:10:00Z', array['disp_on_1','support_on_1']),     -- > 40m, 0

('35', 'l35', 'connected', '2020-06-23T09:10:00Z', array['disp_on_1','support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('35', 'l35', 'disconnected', '2020-06-23T10:00:00Z', DEFAULT, 'connected', '2020-06-23T09:10:00Z', array['disp_on_1','support_on_1']),     -- > 50m, 0

('36', 'l36', 'connected', '2020-06-23T09:10:00Z', array['disp_on_1'], 'disconnected', '2020-06-22T12:00:00Z', DEFAULT),
('36', 'l36', 'disconnected', '2020-06-23T10:10:00Z', DEFAULT, 'connected', '2020-06-23T09:10:00Z', array['disp_on_1']),                    -- > 50m, 0

('37', 'l37', 'connected', '2020-06-23T10:00:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('37', 'l37', 'disconnected', '2020-06-23T10:10:00Z', DEFAULT, 'connected', '2020-06-23T10:00:00Z', array['disp_on_1']),                    -- > 0m, 0

('38', 'l38', 'connected', '2020-06-23T10:10:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('38', 'l38', 'disconnected', '2020-06-23T10:20:00Z', DEFAULT, 'connected', '2020-06-23T10:10:00Z', array['disp_on_1']),                    -- > 0m, 0

('41', 'l41', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('41', 'l41', 'connected', '2020-06-23T09:10:00Z', array['disp_on_1'], 'connected', '2020-06-23T05:00:00Z', array['disp_on_1']),            -- > 1h, 0

('42', 'l42', 'connected', '2020-06-23T05:00:00Z', array['support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('42', 'l42', 'disconnected', '2020-06-23T06:00:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['support_on_1']),                 -- > 0, 0

('43', 'l43', 'connected', '2020-06-23T05:00:00Z', array['support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('43', 'l43', 'disconnected', '2020-06-23T09:00:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['support_on_1']),                 -- > 0, 0

('44', 'l44', 'connected', '2020-06-23T05:00:00Z', array['support_on_1'], DEFAULT, DEFAULT, DEFAULT),
('44', 'l44', 'disconnected', '2020-06-23T09:10:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['support_on_1']),                 -- > 10m, 0

('45', 'l45', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('45', 'l45', 'connected', '2020-06-23T09:10:00Z', DEFAULT, 'connected', '2020-06-23T05:00:00Z', array['disp_on_1']),                       -- > 10m, 0

('51', 'l51', 'disconnected', '2020-06-23T09:20:00Z', DEFAULT, 'connected', '2020-06-23T09:10:00Z', array['support_on_1']),                 -- incorrect order
('51', 'l51', 'connected', '2020-06-23T09:10:00Z', array['support_on_1'], DEFAULT, DEFAULT, DEFAULT),                                       -- > 10m, 0

('52', 'l52', 'connected', '2020-06-23T05:00:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('52', 'l52', 'paused', '2020-06-23T09:10:00Z', array['disp_on_1'], 'connected', '2020-06-23T05:00:00Z', array['disp_on_1']),
('52', 'l52', 'connected', '2020-06-23T09:25:00Z', array['disp_on_1'], 'paused', '2020-06-23T09:10:00Z', array['disp_on_1']),
('52', 'l52', 'disconnected', '2020-06-23T09:45:00Z', array['disp_on_1'], 'connected', '2020-06-23T09:25:00Z', array['disp_on_1']),         -- > 10+20m, 15m

('53', 'l53', 'connected', '2020-06-23T08:50:00Z', array['disp_on_1'], DEFAULT, DEFAULT, DEFAULT),
('53', 'l53', 'connected', '2020-06-23T09:10:00Z', array['support_on_1'], 'connected', '2020-06-23T08:50:00Z', array['disp_on_1']),
('53', 'l53', 'disconnected', '2020-06-23T09:30:00Z', DEFAULT, 'connected', '2020-06-23T09:10:00Z', array['support_on_1']);                -- > 10m/20m

