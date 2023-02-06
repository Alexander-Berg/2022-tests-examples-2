insert into passenger_profile.ratings_sync
(started_at, finished_at, sync_ratings_changed_since, yt_table_name, last_row_processed)
values
-- note that the last sync was not finished (finished_at = null)
('2019-12-15T00:00:00Z', null, '2019-11-15T00:00:00Z', '//home/taxi-analytics/nikmort/user_rating_demo', 12456),

('2019-11-15T00:00:00Z', '2019-11-15T04:00:00Z', '2019-10-15T00:00:00Z', '//home/taxi-analytics/nikmort/user_rating_demo', 123456),
('2019-10-15T00:00:00Z', '2019-11-15T03:00:00Z', null, '//home/taxi-analytics/nikmort/user_rating_demo', 123456)
