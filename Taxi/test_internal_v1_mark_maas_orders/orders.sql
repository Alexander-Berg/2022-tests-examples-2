INSERT INTO maas.orders (
  order_id,   maas_user_id,   phone_id,  
  maas_sub_id,  is_maas_order,  maas_trip_id, 
  from_metro, to_metro
)
VALUES (
  'order_id_success', 'maas_user_id', 'active_phone_id', 
  'maas30000002', true, 'trip_id', 'true', 'false'
),
(
  'order_id_fail', 'maas_user_id', 'active_phone_id', 
  'maas30000002', false, 'trip_id', 'false', 'false'
)
;
