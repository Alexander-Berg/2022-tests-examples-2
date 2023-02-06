INSERT
INTO edc_app_checkups.checkups
(id, number, creator_user_id, creator, driver_id, driver, vehicle_id, vehicle, park_id, park, created_at, passed_at,
 status)
VALUES ('4e991007-5c37-4ef8-a9d5-cf5fef3e4959', '00000000000005721518', '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "display_name": "Петров Семен Семенович"}',
        '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "sex": "male", "license": "1234567890", "last_name": "Петров", "birth_date": "1990-01-07", "first_name": "Семен", "middle_name": "Семенович"}',
        '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
        '{"id": "7a9b5d6f-c0e5-4304-8487-d3981c5852ef", "type": "car", "year": "2005", "model": "Logan", "license_plate": "А001АА"}',
        '2d3d692a-cccd-4f13-acab-f24d11c3b6c3',
        '{"id": "2d3d692a-cccd-4f13-acab-f24d11c3b6c3", "name": "Acme Ltd", "address": "ул. Арбат, 15", "city_id": "02677bb0-e4b6-45a1-a468-2c35c5916422", "primary_state_registration_number": "1037727038315", "phone": "+74852200000", "tz_offset": 3}',
        '2020-04-09 08:25:18.926246', NULL, 'in_progress');

INSERT
INTO edc_app_checkups.checkups
(id, number, creator_user_id, creator, driver_id, driver, vehicle_id, vehicle, park_id, park, created_at, passed_at,
 status)
VALUES ('5e000000-5c37-4ef8-a9d5-cf5fef3e4959', '00000000000005721519', '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "display_name": "Петров Семен Семенович"}',
        '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "sex": "male", "license": "1234567890", "last_name": "Петров", "birth_date": "1990-01-07", "first_name": "Семен", "middle_name": "Семенович"}',
        '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
        '{"id": "7a9b5d6f-c0e5-4304-8487-d3981c5852ef", "type": "car", "year": "2005", "model": "Logan", "license_plate": "А001АА"}',
        '2d3d692a-cccd-4f13-acab-f24d11c3b6c3',
        '{"id": "2d3d692a-cccd-4f13-acab-f24d11c3b6c3", "name": "Acme Ltd", "address": "ул. Арбат, 15", "city_id": "02677bb0-e4b6-45a1-a468-2c35c5916422", "primary_state_registration_number": "1037727038315", "phone": "+74852200000", "tz_offset": 3}',
        '2020-04-09 08:26:18.926246', NULL, 'in_progress');

INSERT
INTO edc_app_checkups.checkups
(id, number, creator_user_id, creator, driver_id, driver, vehicle_id, vehicle, park_id, park, created_at, passed_at,
 status)
VALUES ('4e991007-5c37-4ef8-a9d5-cf5fef3e4988', '00000000000005721528', '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "display_name": "Петров Семен Семенович"}',
        '5328f5a3-cdc2-435d-9c07-672e7dd29fb3',
        '{"id": "5328f5a3-cdc2-435d-9c07-672e7dd29fb3", "sex": "male", "license": "1234567890", "last_name": "Петров", "birth_date": "1990-01-07", "first_name": "Семен", "middle_name": "Семенович"}',
        '7a9b5d6f-c0e5-4304-8487-d3981c5852ef',
        '{"id": "7a9b5d6f-c0e5-4304-8487-d3981c5852ef", "type": "car", "year": "2005", "model": "Logan", "license_plate": "А001АА"}',
        '2d3d692a-cccd-4f13-acab-f24d11c3b6c3',
        '{"id": "2d3d692a-cccd-4f13-acab-f24d11c3b6c3", "name": "Acme Ltd", "address": "ул. Арбат, 15", "city_id": "02677bb0-e4b6-45a1-a468-2c35c5916422", "primary_state_registration_number": "1037727038315", "phone": "+74852200000"}',
        '2020-04-09 08:25:18.926246', NULL, 'in_progress');

INSERT 
INTO edc_app_checkups.technical_reviews 
(id, checkup_id, technician_id, technician, park_id, resolution_is_passed, resolution, passed_at) 
VALUES ('d7ea193b-f122-426d-ac36-91d0c88341be', '4e991007-5c37-4ef8-a9d5-cf5fef3e4959', 
        'fb67a583c14a4db78669f7e0af1fdd26', '{"id": "fb67a583c14a4db78669f7e0af1fdd26", "diploma": "1111", "display_name": "Механиков Механик Механикович"}',
        '11111111cccd4f13acabf24d11c3b6c3',
        true, 
        '{"fields": [{"code": "brakes", "name": "Тормоза", "checked": true, "comment": "LOL"}, {"code": "locks", "name": "Замки", "checked": true}], "odometer_value": 1, "is_passed": true}', 
        '2020-04-09 08:35:57.279901');

UPDATE edc_app_checkups.checkups SET technical_review_id = 'd7ea193b-f122-426d-ac36-91d0c88341be' WHERE id = '4e991007-5c37-4ef8-a9d5-cf5fef3e4959';

INSERT 
INTO edc_app_checkups.medical_reviews 
(id, checkup_id, physician_id, physician, park_id, resolution_is_passed, resolution, passed_at) 
VALUES ('678e70f6-3fd3-46d0-b953-167ef884c004', '4e991007-5c37-4ef8-a9d5-cf5fef3e4959', 
        '3b35047d1d4d4abc903544ffbba00d46', '{"id": "3b35047d1d4d4abc903544ffbba00d46", "display_name": "Врачев Врач Врачевич", "job_position": "фельдшер"}',
        '22222222cccd4f13acabf24d11c3b6c3',
        true, 
        '{"is_passed": true, "heart_rate": 75, "mucous_membranes_are_ok": true, "temperature": {"value": 36.6}, "blood_pressure": {"systolic": 120, "diastolic": 80}}', '2020-04-09 08:49:33.378941');

UPDATE edc_app_checkups.checkups SET medical_review_id = '678e70f6-3fd3-46d0-b953-167ef884c004' WHERE id = '4e991007-5c37-4ef8-a9d5-cf5fef3e4959';

INSERT 
INTO edc_app_checkups.technical_reviews 
(id, checkup_id, technician_id, technician, park_id, resolution_is_passed, resolution, passed_at) 
VALUES ('d7ea193b-f122-426d-ac36-91d0c8834122', '4e991007-5c37-4ef8-a9d5-cf5fef3e4988', 
        'fb67a583c14a4db78669f7e0af1fdd26', '{"id": "fb67a583c14a4db78669f7e0af1fdd26", "diploma": "1111", "display_name": "Механиков Механик Механикович"}',
        '11111111cccd4f13acabf24d11c3b6c3',
        true, 
        '{"fields": [{"code": "brakes", "name": "Тормоза", "checked": true, "comment": "LOL"}, {"code": "locks", "name": "Замки", "checked": true}], "odometer_value": 1, "is_passed": true}', 
        '2020-04-09 08:25:57.279901');

UPDATE edc_app_checkups.checkups SET technical_review_id = 'd7ea193b-f122-426d-ac36-91d0c8834122' WHERE id = '4e991007-5c37-4ef8-a9d5-cf5fef3e4988';

INSERT 
INTO edc_app_checkups.medical_reviews 
(id, checkup_id, physician_id, physician, park_id, resolution_is_passed, resolution, passed_at) 
VALUES ('678e70f6-3fd3-46d0-b953-167ef884c022', '4e991007-5c37-4ef8-a9d5-cf5fef3e4988', 
        NULL, '{"id": "3b35047d1d4d4abc903544ffbba00d46", "display_name": "Врачев Врач Врачевич", "job_position": "фельдшер"}',
        '22222222cccd4f13acabf24d11c3b6c3',
        true, NULL, '2020-04-08 08:49:33.378941');

UPDATE edc_app_checkups.checkups SET medical_review_id = '678e70f6-3fd3-46d0-b953-167ef884c022' WHERE id = '4e991007-5c37-4ef8-a9d5-cf5fef3e4988';
