INSERT INTO
    callcenter_stats.operator_history
    (agent_id, login, status, created_at, queues, prev_status, prev_created_at, prev_queues)
VALUES
-- 05:00 -> 06:00
('11', 'l11', 'disconnected', '2020-01-01T01:00:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0
('12', 'l12', 'disconnected', '2020-01-01T05:30:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0
('13', 'l13', 'disconnected', '2020-01-01T07:00:00Z', DEFAULT, DEFAULT, DEFAULT, DEFAULT),      -- > 0, 0

('21', 'l21', 'connected', '2020-01-01T01:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),     -- > 1h, 0
('22', 'l22', 'connected', '2020-01-01T05:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),     -- > 1h, 0
('23', 'l23', 'connected', '2020-01-01T05:10:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),     -- > 50m, 0
('24', 'l24', 'connected', '2020-01-01T06:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),     -- > 0, 0
('25', 'l25', 'connected', '2020-01-01T07:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),     -- > 0, 0

('31', 'l31', 'connected', '2020-01-01T01:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),
('31', 'l31', 'disconnected', '2020-01-01T02:00:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['disp','support']),   -- > 0, 0

('32', 'l32', 'connected', '2020-01-01T01:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),
('32', 'l32', 'disconnected', '2020-01-01T05:10:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['disp','support']),   -- > 10m, 0

('33', 'l33', 'connected', '2020-01-01T05:00:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),
('33', 'l33', 'disconnected', '2020-01-01T05:50:00Z', DEFAULT, 'connected', '2020-01-01T05:00:00Z', array['disp','support']),   -- > 50m, 0

('34', 'l34', 'connected', '2020-01-01T05:10:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),
('34', 'l34', 'disconnected', '2020-01-01T05:50:00Z', DEFAULT, 'connected', '2020-01-01T05:10:00Z', array['disp','support']),   -- > 40m, 0

('35', 'l35', 'connected', '2020-01-01T05:10:00Z', array['disp','support'], DEFAULT, DEFAULT, DEFAULT),
('35', 'l35', 'disconnected', '2020-01-01T06:00:00Z', DEFAULT, 'connected', '2020-01-01T05:10:00Z', array['disp','support']),   -- > 50m, 0

('36', 'l36', 'connected', '2020-01-01T05:10:00Z', array['disp'], 'disconnected', '2019-12-31T12:00:00Z', DEFAULT),
('36', 'l36', 'disconnected', '2020-01-01T06:10:00Z', DEFAULT, 'connected', '2020-01-01T05:10:00Z', array['disp']),             -- > 50m, 0

('37', 'l37', 'connected', '2020-01-01T06:00:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('37', 'l37', 'disconnected', '2020-01-01T06:10:00Z', DEFAULT, 'connected', '2020-01-01T06:00:00Z', array['disp']),             -- > 0m, 0

('38', 'l38', 'connected', '2020-01-01T06:10:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('38', 'l38', 'disconnected', '2020-01-01T06:20:00Z', DEFAULT, 'connected', '2020-01-01T06:10:00Z', array['disp']),             -- > 0m, 0

('41', 'l41', 'connected', '2020-01-01T01:00:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('41', 'l41', 'connected', '2020-01-01T05:10:00Z', array['disp'], 'connected', '2020-01-01T01:00:00Z', array['disp']),          -- > 1h, 0

('42', 'l42', 'connected', '2020-01-01T01:00:00Z', array['support'], DEFAULT, DEFAULT, DEFAULT),
('42', 'l42', 'disconnected', '2020-01-01T02:00:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['support']),          -- > 0, 0

('43', 'l43', 'connected', '2020-01-01T01:00:00Z', array['support'], DEFAULT, DEFAULT, DEFAULT),
('43', 'l43', 'disconnected', '2020-01-01T05:00:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['support']),          -- > 0, 0

('44', 'l44', 'connected', '2020-01-01T01:00:00Z', array['support'], DEFAULT, DEFAULT, DEFAULT),
('44', 'l44', 'disconnected', '2020-01-01T05:10:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['support']),          -- > 10m, 0

('45', 'l45', 'connected', '2020-01-01T01:00:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('45', 'l45', 'connected', '2020-01-01T05:10:00Z', DEFAULT, 'connected', '2020-01-01T01:00:00Z', array['disp']),                -- > 10m, 0

('51', 'l51', 'disconnected', '2020-01-01T05:20:00Z', DEFAULT, 'connected', '2020-01-01T05:10:00Z', array['support']),          -- incorrect order
('51', 'l51', 'connected', '2020-01-01T05:10:00Z', array['support'], DEFAULT, DEFAULT, DEFAULT),                                -- > 10m, 0

('52', 'l52', 'connected', '2020-01-01T01:00:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('52', 'l52', 'paused', '2020-01-01T05:10:00Z', array['disp'], 'connected', '2020-01-01T01:00:00Z', array['disp']),
('52', 'l52', 'connected', '2020-01-01T05:25:00Z', array['disp'], 'paused', '2020-01-01T05:10:00Z', array['disp']),
('52', 'l52', 'disconnected', '2020-01-01T05:45:00Z', array['disp'], 'connected', '2020-01-01T05:25:00Z', array['disp']),       -- > 10+20m, 15m

('53', 'l53', 'connected', '2020-01-01T04:50:00Z', array['disp'], DEFAULT, DEFAULT, DEFAULT),
('53', 'l53', 'connected', '2020-01-01T05:10:00Z', array['support'], 'connected', '2020-01-01T04:50:00Z', array['disp']),
('53', 'l53', 'disconnected', '2020-01-01T05:30:00Z', DEFAULT, 'connected', '2020-01-01T05:10:00Z', array['support']);          -- > 10m/20m

