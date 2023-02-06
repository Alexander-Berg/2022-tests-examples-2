-- noinspection SqlNoDataSourceInspectionForFile

REPLACE INTO audience_by_device_id 
(device_id, campaign_id) 
VALUES
("iphone", "name-1"),
("android", "name-4");

REPLACE INTO audience_by_personal_phone_id 
(personal_phone_id, campaign_id) 
VALUES
("7896", "name-4"),
("7657", "name-5");

REPLACE INTO audience_by_phone_id 
(phone_id, campaign_id) 
VALUES
("8926", "name-3"),
("8495", "name-2");

REPLACE INTO audience_by_yandex_uid 
(yandex_uid, campaign_id) 
VALUES
("id-1", "name-1"),
("id-2", "name-2");
