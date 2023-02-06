UPDATE checks.arrival
SET eta = make_interval(secs=>1),
    distance = 10,
    air_distance = 25
WHERE check_id = 1601;
