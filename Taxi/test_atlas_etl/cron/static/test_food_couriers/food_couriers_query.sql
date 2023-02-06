SELECT couriers.id as `couriers_id`,
 couriers.location_date as `couriers_location_date`,
 couriers.location_latitude as `couriers_location_latitude`,
 couriers.location_longitude as `couriers_location_longitude`,
 couriers.region_id as `couriers_region_id`,
 couriers.type as `couriers_type`,
 couriers.blocked_until as `couriers_blocked_until`,
 couriers.created_at as `couriers_created_at`,
 courier_active_shift_state.courier_id as `courier_active_shift_state_courier_id`,
 courier_active_shift_state.state as `courier_active_shift_state_state`,
 logistics_ongoing_deliveries_data.place_id as `logistics_ongoing_deliveries_data_place_id`,
 logistics_ongoing_deliveries_data.courier_id as `logistics_ongoing_deliveries_data_courier_id`,
 logistics_ongoing_deliveries_data.status as `logistics_ongoing_deliveries_data_status`,
 regions.name as `regions_name` FROM couriers
LEFT JOIN courier_active_shift_state ON courier_active_shift_state.courier_id = couriers.id
LEFT JOIN logistics_ongoing_deliveries_data ON logistics_ongoing_deliveries_data.courier_id = couriers.id
LEFT JOIN regions ON regions.id = couriers.region_id
WHERE courier_active_shift_state.state IS NOT NULL AND courier_active_shift_state.state != 'closed'
