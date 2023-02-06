INSERT INTO public.countries (code, "name", currency_code, created_at, updated_at)
VALUES ('KG', 'Киргизстан', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('KZ', 'Казахстан', 'KZT', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('TJ', 'Таджикистан', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('UZ', 'Узбекистан', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('BY', 'Белоруссия', 'BYN', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('AM', 'Армения', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('UA', 'Украина', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('GE', 'Грузия', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('TM', 'Туркмения', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('AZ', 'Азербайджан', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000');
INSERT INTO public.countries (code, "name", currency_code, created_at, updated_at)
VALUES ('MD', 'Молдова', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('RU', 'Российская Федерация', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('AB', 'Абхазия', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('AF', 'Афганистан', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('IL', 'Израиль', 'ILS', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('LV', 'Латвия', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('LT', 'Литва', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('OS', 'Осетия', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('EE', 'Эстония', 'RUB', '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('FR', 'Франция', 'EUR', '2021-04-14 10:50:52.000', '2021-04-14 10:50:52.000');

INSERT INTO public.currencies (code, "name", symbol, decimal_places, created_at, updated_at)
VALUES ('BYN', 'Belarusian Ruble', 'Br', 2, '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('KZT', 'Tenge', '₸', 2, '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('RUB', 'Rouble', '₽', 2, '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('ILS', 'Israeli new shekel', '₪', 2, '2020-10-12 10:52:37.000', '2020-10-12 10:52:37.000'),
       ('EUR', 'Euro', '€', 2, '2021-04-14 10:50:52.000', '2021-04-14 10:50:52.000');

INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO public.couriers (id, group_id, region_id, courier_type, name, work_status, created_at, updated_at,
                             service, external_id, pool_name, logistics_group_id, birthday, is_storekeeper,
                             is_dedicated_picker, is_picker, use_logistics_group_for_unplanned_shifts)
VALUES (1, 1, 1, 'pedestrian', 'test', 'active', NOW(), NOW(), 'driver-profiles', '456_123', NULL, 1, '11-09-1991', false, false, false, false);


INSERT INTO public.regions (id, name, time_zone_vs_moscow, country_code, created_at, updated_at)
VALUES (1, 'Moscow', 0, 'RU', NOW(), NOW());

INSERT INTO point_start_list (point_start_id, city_id, point_start_name, point_start_status, zone_ff_time_add,
                              metagroup_id, group_id, created_at, updated_at)
VALUES (6341, 1, 'Крылатское - Молодежная', 1, 1561840818, NULL, NULL, '2020-11-12T14:34:17.000',
        '2021-04-14T18:57:17.000');

INSERT INTO point_start_list (point_start_id,city_id,point_start_name,point_start_status,zone_ff_time_add,metagroup_id,group_id,created_at,updated_at) VALUES
	 (6596,1,'Арбатская - Третьяковская',1,1561840818,NULL,3,'2020-11-12T14:34:17.000','2021-08-27T18:32:19.000');

INSERT INTO courier_shifts (id,courier_offline_time,courier_id,updated_at,status,has_lateness,has_early_leaving,is_abandoned,region_id,zone_id,start_time,end_time,"date",courier_type,parent_id,courier_assigned_at,created_at,mass_upload_id,"type",external_id,is_zone_checked,guarantee,pool,logistics_group_id,effective_logistics_group_id,start_location_id,service) VALUES
(1,0,1,now(),'planned',false,false,false,1,6341,current_date + time '23:59', TIMESTAMP 'tomorrow' + time '03:00',current_date,1,NULL,now() - '1 minute'::interval,now() + '1 hour'::interval,NULL,'planned',NULL,true,NULL,'courier',NULL,NULL,NULL,'eda')
;

INSERT INTO courier_shift_change_requests (shift_id,changeset,is_approved,updated_at,created_at) VALUES
	 (1,'{"offers": [{"id": "1", "deliveryZoneId":6596}]}',NULL,now() - '1 minute'::interval,now() - '1 minute'::interval);
