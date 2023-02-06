DO $$
DECLARE
base_point JSONB :=  '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }';
base_interim_destinations JSONB[] := '{"{\"fullname\": \"Россия, Москва, Тверская улица, 18к1\", \"geopoint\": [37.6039000014267, 55.7657515910581]}","{\"fullname\": \"Россия, Москва, Суворовская площадь, 1/52к1\", \"geopoint\": [37.614706734294667, 55.7814989936165]}"}';
base_personal_phone_id VARCHAR(40) := 'personal_phone_id';
base_status TEXT := 'finished';
BEGIN

INSERT INTO corp_combo_orders.deliveries
(id, client_id, route_type, common_point)
VALUES
    ('delivery_id_1', 'client_id_1', 'ONE_A_MANY_B', base_point),
    ('delivery_id_2', 'client_id_1', 'ONE_A_MANY_B', base_point),
    ('delivery_id_3', 'client_id_2', 'ONE_A_MANY_B', base_point);

INSERT INTO corp_combo_orders.orders
(id, delivery_id, due_date, finished_date, personal_phone_id, source, destination, interim_destinations, status)
VALUES
    ('order_id_1', 'delivery_id_1', '2021-09-14T20:30:15+0000'::timestamptz, '2021-09-14T21:00:25+0000'::timestamptz, base_personal_phone_id, base_point, base_point, base_interim_destinations, base_status),
    ('order_id_2', 'delivery_id_1', '2021-09-14T20:30:25+0000'::timestamptz, '2021-09-14T21:00:15+0000'::timestamptz, base_personal_phone_id, base_point, base_point, base_interim_destinations, base_status),
    ('order_id_3', 'delivery_id_2', '2021-09-15T20:30:15+0000'::timestamptz, '2021-09-15T21:00:15+0000'::timestamptz, base_personal_phone_id, base_point, base_point, base_interim_destinations, base_status),
    ('order_id_4', 'delivery_id_3', '2021-09-15T20:30:15+0000'::timestamptz, '2021-09-15T21:00:15+0000'::timestamptz, base_personal_phone_id, base_point, base_point, base_interim_destinations, base_status);

INSERT INTO corp_combo_orders.order_points
(order_id, user_personal_phone_id, point)
VALUES
    ('order_id_1', 'user_phone_id_1', base_point),
    ('order_id_1', 'user_phone_id_2', base_point),
    ('order_id_2', 'user_phone_id_3', base_point),
    ('order_id_3', 'user_phone_id_1', base_point),
    ('order_id_3', 'user_phone_id_3', base_point),
    ('order_id_4', 'user_phone_id_1', base_point);

END
$$;

