INSERT INTO qc_photo.tasks (type, name, description, storage_type)
VALUES ('hands_free_handover', 'Бесконтактная передача', 'Фото, подтверждающее бесконтактную передачу заказа клиенту', 's3'),
       ('courier_selfie_with_doc', 'Фото лица курьера', 'Селфи курьера с докуметом, подтверждающим личность', 'avatarnica')
;

INSERT INTO qc_photo.subtasks (task_id, type, name, description, path_to_example_image)
VALUES (1, 'hands_free_handover', 'Руки проч передача', 'Фото, подтверждающее бесконтактную передачу заказа клиенту', NULL),
       (2, 'courier_selfie_with_doc', 'Селфак курьера', 'Селфи курьера с докуметом, подтверждающим личность', NULL),
       (2, 'courier_health_permit', 'Главная страница медкнижки', 'Пришлите фото главной страницы медкнижки', 'courier_health_permit_example')
;
