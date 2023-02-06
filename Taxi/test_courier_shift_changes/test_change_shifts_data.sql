SET TIME ZONE 'Europe/Moscow';

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

INSERT INTO courier_shifts
(id, courier_offline_time, courier_id, region_id, zone_id, start_time, end_time, date, guarantee, start_location_id)
VALUES
    (1, 1, 1, 1, 1, '2021-08-06T10:20:00Z', '2021-08-06T20:40:00Z', '2021-08-06', '120.00', 1),
    (2, 1, 2, 2, 2, '2021-08-06T20:20:00Z', '2021-08-06T23:40:00Z', '2021-08-06', '120.50', NULL),
    (3, 1, 3, 3, 3, '2021-08-06T02:20:00Z', '2021-08-06T08:40:00Z', '2021-08-06', NULL, NULL),
    (4, 1, 4, 3, 3, '2021-08-06T05:20:00Z', '2021-08-06T08:40:00Z', '2021-08-05', NULL, NULL),
    (5, 1, 5, 4, 3, '2021-08-06T08:20:00Z', '2021-08-06T09:40:00Z', '2021-08-05', NULL, NULL),
    (6, 1, 6, 5, 3, '2021-08-06T08:20:00Z', '2021-08-06T20:40:00Z', '2021-08-06', NULL, NULL),
    (7, 1, 7, 1, 1, '2021-08-06T08:20:00Z', '2021-08-06T23:40:00Z', '2021-08-06', NULL, NULL);

INSERT INTO point_start_list
(point_start_id, city_id, point_start_name)
VALUES
    (1, 1, 'Moscow/DeliveryZone'),
    (2, 2, 'Shanghai/DeliveryZone'),
    (3, 3, 'New_York/DeliveryZone');

INSERT INTO courier_shift_change_requests
(shift_id, changeset, updated_at)
VALUES
    (1, '{"offers": [{"id": "1", "startTime":"08:00"},{"id": "2", "endTime":"21:40"}]}', '2021-08-06T01:40:00Z'),
    (2, '{"offers": [{"id": "1", "endTime":"16:00"}]}', '2021-08-06T01:40:00Z'),
    (3, '{"offers": [{"id": "1", "startTime":"08:00", "endTime":"16:00", "deliveryZoneId":2}]}', '2021-08-06T01:40:00Z'),
    (4, '{"offers": [{"id": "1", "endTime":"16:00"}]}', '2021-08-06T01:40:00Z'),
    (5, '{"offers": [{"id": "1", "endTime":"18:00"}]}', '2021-08-07T01:40:00Z'),
    (6, '{"offers": [{"id": "1", "endTime":"18:00"}]}', '2021-08-07T01:40:00Z'),
    (7, '{"offers": [{"id": "1", "endTime":"03:00"}]}', '2021-08-07T01:40:00z');

INSERT INTO regions
(id, name, time_zone_vs_moscow, country_code)
VALUES
    (1, 'Moscow', 0, 'RU'),
    (2, 'City+5', 5, 'RU'),
    (3, 'City-7', -7, 'RU'),
    (4, 'City-3', -3, 'RU'),
    (5, 'City+2', 2, 'RU');

INSERT INTO courier_start_location_availability_flags
(id, courier_id, flag_name)
VALUES
    (1, 1, 'flag');

INSERT INTO start_locations (id, region_id, name, latitude, longitude, created_at, updated_at)
VALUES
       (1, 1, 'Moscow location', 55.752518, 37.620595, '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z');

INSERT INTO courier_groups
(id, name)
VALUES (1, 'courier_group');

INSERT INTO couriers
(id, group_id, region_id, courier_type, name, work_status, created_at, updated_at, service, external_id, pool_name)
VALUES
    (1, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID', 'POOL_NAME'),
    (2, 1, 1, 'pedestrian', 'Petya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_2', 'POOL_NAME'),
    (3, 1, 1, 'bicycle', 'Ivan', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_3', 'POOL_NAME'),
    (4, 1, 3, 'pedestrian', 'Artem', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_4', 'POOL_NAME'),
    (5, 1, 4, 'bicycle', 'Vadim', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_5', 'POOL_NAME'),
    (6, 1, 5, 'bicycle', 'Vadim', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_6', 'POOL_NAME'),
    (7, 1, 1, 'pedestrian', 'Vasya', 'active', '2020-11-27T18:41:25Z', '2020-11-27T18:41:25Z', 'eats', 'EXTERNAL_ID_7', 'POOL_NAME');

