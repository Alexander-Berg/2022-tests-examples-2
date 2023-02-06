insert into couriers (id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service,
                      external_id, pool_name, logistics_group_id, birthday, is_storekeeper, is_dedicated_picker,
                      is_picker, use_logistics_group_for_unplanned_shifts, is_park_courier, is_rover,
                      is_fixed_shifts_option_enabled)
values (1, 1, 1, 'pedestrian', 'test_courier_1', 'active', '2021-04-21 15:06:13', '2022-01-11 14:16:58',
        'driver-profiles', '0253f79a86d14b7ab9ac1d5d3017be47_901ab3bdabc34d1435e15c6c789424b1', 'lavka', 1,
        '1977-04-21', false, false, false, true, false, false, false),
       (2, 1, 1, 'pedestrian', 'test_courier_2', 'active', '2021-05-25 14:11:15', '2022-01-11 19:57:08',
        'driver-profiles', '0253f79a86d14b7ab9ac1d5d3017be47_475e33ce4e3f69607f078314b94a6b89', 'lavka', 1,
        '1979-04-09', false, false, false, true, false, false, false),
       (3, 1, 1, 'pedestrian', 'test_courier_3', 'active', '2021-09-29 11:23:17', '2022-01-11 19:41:09',
        'driver-profiles', '0253f79a86d14b7ab9ac1d5d3017be47_2194bc5f9e6634361c787a6ba424f824', 'eda', null,
        '1995-01-01', false, false, false, true, false, false, false),
       (4, 1, 1, 'pedestrian', 'test_courier_4', 'active', '2021-11-19 17:44:44', '2022-01-11 20:43:12',
        'driver-profiles', 'e3f66bc7ca3648e5a7c81ca01130d30c_462456d798f48b0a29e62730599e1c44', 'eda', null,
        '1993-11-11', false, false, false, true, false, false, false),
       (5, 1, 1, 'pedestrian', 'test_courier_no_driver_id', 'active', '2021-04-21 14:01:15', '2022-01-11 14:16:58',
        'driver-profiles', null, 'eda', null,
        '1976-04-22', false, false, false, true, false, false, false),
       (6, 1, 1, 'pedestrian', 'test_courier_no_position', 'active', '2021-04-21 15:06:13', '2022-01-11 14:16:58',
        'driver-profiles', '0253f79a86d14b7ab9ac1d5d3017be47_901ab3bdabc34d1435e15c6c789424b2', 'eda', null,
        '1977-04-21', false, false, false, true, false, false, false);

insert into courier_shifts (id, courier_offline_time, courier_id, updated_at, status, has_lateness, has_early_leaving,
                            is_abandoned, region_id, zone_id, start_time, end_time, date, courier_type, parent_id,
                            courier_assigned_at, created_at, mass_upload_id, type, external_id, is_zone_checked,
                            guarantee, pool, logistics_group_id, effective_logistics_group_id, start_location_id,
                            service)
values (1, 0, 1, '2022-01-11 10:34:24', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:29:34',
        '2022-01-11 11:29:34', '2022-01-11', 1, null, null, '2022-01-11 10:29:34', null, 'unplanned', null, true, null,
        'courier', null, 1, null, 'lavka'),
       (2, 0, 2, '2022-01-11 10:24:27', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:19:58',
        '2022-01-11 11:19:58', '2022-01-11', 1, null, null, '2022-01-11 10:19:59', null, 'unplanned', null, true, null,
        'courier', null, 1, null, 'lavka'),
       (3, 0, 3, '2022-01-11 10:24:27', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:19:52',
        '2022-01-11 22:19:52', '2022-01-11', 1, null, null, '2022-01-11 10:19:53', null, 'unplanned', null, true, null,
        'courier', null, null, null, 'eda'),
       (4, 0, 4, '2022-01-11 10:04:26', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:00:06',
        '2022-01-11 11:00:06', '2022-01-11', 1, null, null, '2022-01-11 10:00:07', null, 'planned', null, true, null,
        'courier', null, null, null, 'eda'),
       (5, 0, 5, '2022-01-11 10:24:27', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:19:52',
        '2022-01-11 22:19:52', '2022-01-11', 1, null, null, '2022-01-11 10:10:53', null, 'unplanned', null, true, null,
        'courier', null, null, null, 'eda'),
       (6, 0, 6, '2022-01-11 10:24:27', 'in_progress', false, false, false, 1, 1, '2022-01-11 10:19:52',
        '2022-01-11 22:19:52', '2022-01-11', 1, null, null, '2022-01-11 10:00:53', null, 'unplanned', null, true, null,
        'courier', null, null, null, 'eda');

insert into courier_shift_states (id, shift_id, started_at, finished_at, duration, updated_at, pause_duration,
                                  created_at)
values (1, 1, '2022-01-11 10:29:34', null, null, '2022-01-13 10:29:35', null, '2022-01-11 10:29:35'),
       (2, 2, '2022-01-11 10:19:58', null, null, '2022-01-13 10:19:59', null, '2022-01-11 10:19:59'),
       (3, 3, '2022-01-11 10:19:52', null, null, '2022-01-13 10:19:53', null, '2022-01-11 10:19:53'),
       (4, 4, '2022-01-11 10:00:06', null, null, '2022-01-13 10:00:07', null, '2022-01-11 10:00:07'),
       (5, 5, '2022-01-11 10:13:06', null, null, '2022-01-13 10:13:07', null, '2022-01-11 10:13:07'),
       (6, 6, '2022-01-11 10:07:06', null, null, '2022-01-13 10:07:07', null, '2022-01-11 10:07:07');

insert into courier_states (courier_id, state, updated_at, last_online, is_busy, approximate_busy_until, last_busy_at)
values (1, 'online', '2022-01-11 16:07:08', null, true, null, '2022-01-11 10:45:03'),
       (2, 'online', '2022-01-11 18:04:09', null, false, null, '2022-01-11 10:35:58'),
       (3, 'online', '2022-01-11 18:04:09', null, false, null, '2021-12-21 14:06:13'),
       (4, 'online', '2022-01-11 18:05:10', null, false, null, '2021-12-28 16:24:12'),
       (5, 'online', '2022-01-11 18:05:10', null, false, null, '2021-12-28 16:24:12'),
       (6, 'online', '2022-01-11 18:05:10', null, false, null, '2021-12-28 16:24:12');


insert into courier_shift_events (id, shift_id, event_type, event_source, latitude, longitude, created_at, courier_id,
                                  registered_at)
values (1, 1, 'started', 'courier', 55.769851, 37.630661, '2022-01-11 10:00:00', 1, '2022-01-11 10:00:00'),
       (2, 2, 'started', 'courier', 55.760150, 37.529442, '2022-01-11 10:00:00', 2, '2022-01-11 10:00:00'),
       (3, 3, 'started', 'courier', 55.887786, 37.505032, '2022-01-11 10:00:00', 3, '2022-01-11 10:00:00'),
       (4, 4, 'started', 'courier', 55.787330, 37.742022, '2022-01-11 10:00:00', 4, '2022-01-11 10:00:00'),
       (5, 5, 'started', 'courier', 55.787430, 37.743022, '2022-01-11 10:00:00', 4, '2022-01-11 10:00:00'),
       (6, 6, 'started', 'courier', 55.787530, 37.741022, '2022-01-11 10:00:00', 4, '2022-01-11 10:00:00');
