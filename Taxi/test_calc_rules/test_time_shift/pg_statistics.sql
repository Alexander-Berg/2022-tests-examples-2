INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2021-11-15 11:59:40+0000', 'client', 'timeshift.test.created', 10),
('2021-11-15 11:59:50+0000', 'client', 'timeshift.test.updated', 10),
('2021-11-15 12:00:00+0000', 'client', 'timeshift.test.created', 50),
('2021-11-15 12:00:00+0000', 'client', 'timeshift.test.updated', 50),
('2021-11-15 12:00:00+0000', 'client', 'timeshift.test.found',   10);
