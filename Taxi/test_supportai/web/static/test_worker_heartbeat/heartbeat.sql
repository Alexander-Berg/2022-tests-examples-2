INSERT INTO supportai.heartbeats (host, worker_id, updated_at)
VALUES
('expired.localhost', '0', now() - INTERVAL '2 DAYS')
