INSERT INTO corp_combo_orders.route_tasks
    (id, idempotency_token, client_id, external_route_task_id, route_type, task_status, common_point)
VALUES
    ('route_task_1', 'e98858cb-d778-4d76-89e2-635728334138', 'client_id_1', 'routing_task_id_1', 'ONE_A_MANY_B', 'done', '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'),
    ('route_task_2', '02a16be7-52b8-436b-a60c-7351fca105d3', 'client_id_1', NULL , 'ONE_A_MANY_B', 'queued', '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'),
    ('route_task_3', 'b3265ed9-99cf-488e-88bc-e84ce32d31e3', 'client_id_1', 'routing_task_id_3', 'ONE_A_MANY_B', 'failed', '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }'),
    ('route_task_4', '52f56418-3ece-4ec2-9454-82df4da6aa28', 'client_id_2', 'routing_task_id_4', 'ONE_A_MANY_B', 'failed', '{ "geopoint": [1, 2], "fullname": "Россия, Москва, Большая Никитская улица, 13" }');

INSERT INTO corp_combo_orders.route_task_points
    (route_task_id, user_personal_phone_id, point, route_number, number_in_route)
VALUES
    ('route_task_1', 'personal_1', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', 0, 2),
    ('route_task_1', 'personal_2', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', 0, 1),
    ('route_task_1', 'personal_3', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', 1, 1),
    ('route_task_1', 'personal_4', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', 1, 3),
    ('route_task_1', 'personal_5', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', 1, 2),
    ('route_task_2', 'personal_6', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', NULL, NULL),
    ('route_task_2', 'personal_7', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', NULL, NULL),
    ('route_task_2', 'personal_8', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', NULL, NULL),
    ('route_task_3', 'personal_8', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', NULL, NULL),
    ('route_task_4', 'personal_8', '{ "geopoint": [1, 3], "fullname": "Россия, Москва, Большая Никитская улица, 13" }', NULL, NULL);
