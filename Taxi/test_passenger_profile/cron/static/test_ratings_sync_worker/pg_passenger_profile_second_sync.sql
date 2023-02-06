insert into passenger_profile.ratings_sync
(started_at, finished_at, sync_ratings_changed_since, yt_table_name, last_row_processed)
values
('2019-12-15T00:00:00Z', null, '2019-12-01T13:00:00Z', '//home/ratings', 0),
('2019-12-01T13:00:00Z', '2019-11-15T04:00:00Z', null, '//home/taxi-analytics/nikmort/user_rating_demo', 123456);

insert into passenger_profile.profile (yandex_uid, brand, first_name, rating)
values
('101762215', 'yango', 'Алексей', 5.00),
('184015124', 'yauber', 'Михаил', 5.00),
('247584758', 'yataxi', 'Александр', 5.00),
('24870362', 'yataxi', 'Анастасия', 5.00),
('28741312', 'yataxi', 'Анна', 5.00);
