insert into taxi_surger_revisions (id, created_at, committed_at, partition_name)
values
(1, '2021-02-20T10:05:41+00:00','2021-02-20T10:05:00+00:00','taxi_surger_parts_06'),
(9, '2021-02-20T10:00:41+00:00','2021-02-20T10:00:41+00:00','taxi_surger_parts_06'),
(10, '2021-02-20T10:00:41+00:00','2021-02-20T10:10:41+00:00','taxi_surger_parts_06');


insert into taxi_surger_parts_06 (id, calculator_name, place_id, result, revision_id)
values
(1, 'calc_surge_eats_2100m', 1, '{"free":0,"load_level":85,"busy":0,"delivery_fee":399,"surge_level":3,"additional_time_percents":30, "extra": {"taxi_surge_level": 2, "taxi_show_radius": 500, "taxi_delivery_fee": 59.9} }',1), -- native
(2, 'calc_surge_eats_2100m', 2, '{"free":0,"load_level":85,"busy":0,"delivery_fee":199,"surge_level":3,"additional_time_percents":30,"extra": {"show_radius": 100.0} }',1), -- native
(3, 'calc_surge_eats_2100m', 3, '{"free":0,"load_level":85,"busy":0,"delivery_fee":299,"surge_level":3,"additional_time_percents":30,"extra": {} }',1); -- native
