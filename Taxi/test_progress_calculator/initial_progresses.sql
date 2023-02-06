-- NOW IS '2020-11-01T00:00:00+03:00'::TIMESTAMPTZ

INSERT INTO random_bonus.progress
(park_id, driver_id, progress, is_first, last_status,
 status_updated_at,
 last_online_at,
 last_bonus_at)
VALUES -- ordered by last_online_at desc
-- gets progress online, first box
('park1', 'driver1', 0, TRUE, 'online',
 '2020-10-31T23:59:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T23:58:59.999+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- doesnt get progress offline
('park2', 'driver2', 15, TRUE, 'offline',
 '2020-10-31T23:59:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T23:58:59.998+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- gets progress onorder, not the first box
('park3', 'driver3', 50, FALSE, 'onorder',
 '2020-10-31T23:59:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T23:58:59.997+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- turns online after a short break, saves progress
('park4', 'driver4', 85, FALSE, 'offline',
 '2020-10-31T23:59:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T22:30:00+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- turns online after a long break, loses progress
('park5', 'driver5', 80, FALSE, 'offline',
 '2020-10-31T21:35:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T21:30:00+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- finishes the progress, got the bonus
('park6', 'driver6', 99.95, TRUE, 'onorder',
 '2020-10-31T23:59:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T23:58:59.996+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ),

-- driver7 intentionally skipped

-- updated too long ago - even no request for status
('park8', 'driver8', 77, FALSE, 'offline',
 '2020-10-31T17:00:00+03:00'::TIMESTAMPTZ,
 '2020-10-31T17:00:00+03:00'::TIMESTAMPTZ,
 '2020-01-01T00:00:00+03:00'::TIMESTAMPTZ)
;
