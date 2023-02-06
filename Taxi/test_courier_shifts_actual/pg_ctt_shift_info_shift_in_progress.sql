INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO public.couriers (id, group_id, region_id, courier_type, name, work_status, created_at, updated_at,
                             service, external_id, pool_name, logistics_group_id, birthday, is_storekeeper, is_park_courier,
                             is_dedicated_picker, is_picker, use_logistics_group_for_unplanned_shifts)
VALUES (1, 1, 1, 'pedestrian', 'test', 'active', NOW(), NOW(), 'driver-profiles', '456_123', NULL, 1, '11-09-1991', false, false, false, false, false);


INSERT INTO public.regions (id, name, time_zone_vs_moscow, country_code, created_at, updated_at)
VALUES (1, 'Moscow', 0, 1, NOW(), NOW());

INSERT INTO point_start_list (point_start_id, city_id, point_start_name, point_start_status, zone_ff_time_add,
                              metagroup_id, group_id, created_at, updated_at)
VALUES (6341, 1, 'Крылатское - Молодежная', 1, 1561840818, NULL, NULL, '2020-11-12 14:34:17.000',
        '2021-04-14 18:57:17.000');

INSERT INTO courier_shift_total_durations (courier_id, start_at, finish_at, created_at, updated_at) VALUES (1, current_date, current_date + 1, NOW(), NOW());

INSERT INTO courier_shifts (id,courier_offline_time,courier_id,updated_at,status,has_lateness,has_early_leaving,is_abandoned,region_id,zone_id,start_time,end_time,"date",courier_type,parent_id,courier_assigned_at,created_at,mass_upload_id,"type",external_id,is_zone_checked,guarantee,pool,logistics_group_id,effective_logistics_group_id,start_location_id,service) VALUES
(1,0,1, now(),'in_progress',false,false,false,1,6341,now() - '1 minute'::interval,now() + '3 hour'::interval,current_date,1,NULL,NULL,now() - '1 minute'::interval,NULL,'unplanned',NULL,true,NULL,'courier',NULL,NULL,NULL,'eda')
;

INSERT INTO courier_shift_events (shift_id,event_type,event_source,latitude,longitude,created_at,courier_id,registered_at) VALUES
(1,'started','courier',55.727087,37.625217,now() - '1 minute'::interval,1,now() - '1 minute'::interval)
;
INSERT INTO courier_states (courier_id,state,updated_at,last_online,is_busy,approximate_busy_until,last_busy_at) VALUES
(1,'online',now(),NULL,false,NULL,NULL)
;

INSERT INTO courier_active_shifts (courier_id,shift_id,state,high_priority,zone_id,metagroup_id,zone_group_id,unpauses_at,closes_at,started_at,created_at,updated_at,paused_at) VALUES
(1,1,'in_progress',false,6341,NULL,NULL,NULL,now() + '3 hour'::interval,now() - '1 minute'::interval,now() - '1 minute'::interval,now(),NULL)
;

INSERT INTO courier_shift_states (shift_id,started_at,finished_at,duration,updated_at,pause_duration,created_at) VALUES
	 (1,now() - '1 minute'::interval,NULL,NULL,now() - '1 minute'::interval,NULL,now() - '1 minute'::interval);

INSERT INTO region_settings (id, region_id,"name","value","type",updated_at,created_at) VALUES
(1, 1,'delayed_pause_availability','0','bool','2021-01-22 12:03:13.000','2021-01-21 19:42:35.000')
,(7, 1,'pause_max_count','20','unsigned_int','2021-02-10 14:43:05.000','2019-02-28 11:09:36.000')
,(8, 1,'pause_start_shift_end_threshold','60','unsigned_int','2019-09-18 15:39:24.000','2019-09-18 15:39:24.000')
,(9, 1,'pause_workload_threshold','101','unsigned_int','2021-01-21 21:04:43.000','2019-02-28 11:09:36.000')
;
