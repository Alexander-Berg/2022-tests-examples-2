INSERT INTO cargo_claims.points (
    id, longitude, latitude, fullname, created_ts, 
    updated_ts, contact_name, contact_personal_phone_id,
    city, street, building, external_order_id)
VALUES
    (101, 37.9, 55.8, 'fullname', '2020-01-27T15:35:00+0000',
     '2020-01-27T15:35:00+0000', 'contact', '+70009050401_id',
     NULL, NULL, NULL, NULL),
    (102, 37.9, 55.8, 'fullname', '2020-01-27T15:40:00+0000',
     '2020-01-27T15:40:00+0000', 'contact', '+70009050402_id',
     NULL, NULL, NULL, '54321'),
    (103, 37.9, 55.8, 'fullname', '2020-01-27T15:50:00+0000',
     '2020-01-27T15:50:00+0000', 'contact', '+70009050403_id',
     NULL, NULL, NULL, '12345'),
    (104, 37.9, 55.8, 'fullname', '2020-01-27T15:55:00+0000',
     '2020-01-27T15:55:00+0000', 'contact', '+70009050404_id',
     'City1', 'Street1', 'Building1', NULL),
    (105, 37.9, 55.8, 'fullname', '2020-01-27T15:55:00+0000',
     '2020-01-27T15:55:00+0000', 'contact', '+70009050405_id',
     'City2', 'Street2', 'Building2', NULL),
    (106, 37.9, 55.8, 'fullname', '2020-01-27T15:55:00+0000',
     '2020-01-27T15:55:00+0000', 'contact', '+70009050405_id',
     'City3', 'Street3', 'Building3', NULL)
;
