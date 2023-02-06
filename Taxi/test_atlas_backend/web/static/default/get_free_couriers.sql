SELECT
    suppliers.external_id AS courier_id,
    suppliers.travel_type AS courier_type,
    suppliers.name AS courier_name,
    couriers.location_latitude AS courier_lat,
    couriers.location_longitude AS courier_lon,
    IF(logistic_place_groups.meta_group IS NULL, 'eda', logistic_place_groups.meta_group) AS courier_source,
    IF(logistics_ongoing_deliveries_data.courier_id IS NULL,
        'free',
        logistics_ongoing_deliveries_data.status) AS courier_status,
    LEAST(TIMESTAMPDIFF(SECOND, COALESCE(last_orders_info.updated_at, '1970-01-01'), NOW()),
          TIMESTAMPDIFF(SECOND, suppliers.created_at, NOW()),
          14400) AS free_time,
    IF(suppliers.subtype = 'planned', 'plan', 'free') AS shift_type,
    logistics_ongoing_deliveries_data.source_latitude AS restaurant_lat,
    logistics_ongoing_deliveries_data.source_longitude AS restaurant_lon,
    logistics_ongoing_deliveries_data.destination_latitude AS order_lat,
    logistics_ongoing_deliveries_data.destination_longitude AS order_lon,
    places.name AS restaurant_name,
    places.address_short AS restaurant_address,
    IF(logistics_ongoing_deliveries_data.courier_id IS NULL,
       NULL,
       COALESCE(orders.address_short,
             CONCAT(COALESCE(orders.address_city, ''), ', ',
                    COALESCE(orders.address_street, ''), ', ',
                    COALESCE(orders.address_house, '')))) AS order_address,
    orders.order_nr AS order_id
FROM suppliers
INNER JOIN couriers ON couriers.id = suppliers.external_id
AND couriers.location_latitude between 55.74978423956397 and 55.76259849386081
AND couriers.location_longitude between 37.620213031768806 and 37.63439655303956
LEFT JOIN logistics_ongoing_deliveries_data ON logistics_ongoing_deliveries_data.courier_id = suppliers.external_id
LEFT JOIN logistic_place_groups ON suppliers.logistic_place_group_id = logistic_place_groups.id
LEFT JOIN (
        SELECT courier_id, MAX(updated_at) AS updated_at
        FROM orders
        WHERE orders.updated_at >= DATE_SUB(NOW(), INTERVAL 14400 SECOND )
        GROUP BY courier_id
    ) AS last_orders_info
    ON last_orders_info.courier_id = suppliers.external_id
LEFT JOIN places ON logistics_ongoing_deliveries_data.place_id = places.id
LEFT JOIN order_delivery_info ON logistics_ongoing_deliveries_data.id = order_delivery_info.id
LEFT JOIN orders ON orders.id = order_delivery_info.order_id;
