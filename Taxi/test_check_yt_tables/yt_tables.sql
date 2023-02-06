INSERT INTO fleet_drivers_scoring.yt_updates(name, path, created_at, revision)
VALUES (UNNEST(array ['orders', 'quality_metrics', 'ratings', 'high_speed_driving', 'passenger_tags', 'driving_style']::fleet_drivers_scoring.yt_update_name[]),
        'test_path', '2020-05-17T03:00'::TIMESTAMP, '2020-05-17T03:00'::TIMESTAMP);
