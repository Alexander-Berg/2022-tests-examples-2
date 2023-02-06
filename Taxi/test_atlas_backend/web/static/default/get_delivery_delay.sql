SELECT orders.order_nr as order_id,
       IF(orders.processing_type = 'store', 'lavka', 'eda') as order_type,
       orders.location_latitude as order_lat,
       orders.location_longitude as order_lon,
       places.location_latitude as restaurant_lat,
       places.location_longitude as restaurant_lon,
       couriers.id as courier_id,
       couriers.type as courier_type,
       couriers.username as courier_name,
       couriers.location_latitude as courier_lat,
       couriers.location_longitude as courier_lon,
       logistics_ongoing_deliveries_data.status as courier_status,
       CASE
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.max_place_arrival_time,
               NOW()
               ) > 300
               AND del_info.actual_arrived_to_place is NULL
               THEN 'on_the_way_to_restaurant'
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.actual_arrived_to_place,
               NOW()
               ) > 300
               AND (order_status_history.status = 'ready' OR integration_order_statuses.status = 'finish')
               AND del_info.actual_order_taken is NULL
               THEN 'in_restaurant'
           WHEN TIMESTAMPDIFF(SECOND,
               COALESCE(del_info.actualized_customer_arrival_time,del_info.max_customer_arrival_time),
               NOW()
               ) > 300
               AND del_info.actual_arrived_to_customer is NULL
               THEN 'on_the_way_to_client'
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.actual_arrived_to_customer,
               NOW()
               ) > 300
               AND orders.status != 4
               THEN 'transfer_to_customer'
            WHEN orders.processing_type = 'store' AND suppliers.logistic_place_group_id != logistic_place_groups_places.logistic_place_group_id
               THEN 'another_lavka_place_group'
            WHEN
               ((orders.processing_type = "native" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 1500)
                OR (orders.processing_type = "fast_food" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 2100)
                OR (orders.processing_type = "store" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 480))
                THEN 'known_in_advance_lateness'
       END as order_delay_type,
       CASE
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.max_place_arrival_time,
               NOW()
               ) > 300
               AND del_info.actual_arrived_to_place is NULL
               THEN TIMESTAMPDIFF(SECOND, del_info.max_place_arrival_time, NOW())
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.actual_arrived_to_place,
               NOW()
               ) > 300
               AND (order_status_history.status = 'ready' OR integration_order_statuses.status = 'finish')
               AND del_info.actual_order_taken is NULL
               THEN TIMESTAMPDIFF(SECOND, del_info.actual_arrived_to_place, NOW())
           WHEN TIMESTAMPDIFF(SECOND,
               COALESCE(del_info.actualized_customer_arrival_time,del_info.max_customer_arrival_time),
               NOW()
               ) > 300
               AND del_info.actual_arrived_to_customer is NULL
               THEN TIMESTAMPDIFF(SECOND,
                                  COALESCE(del_info.actualized_customer_arrival_time,del_info.max_customer_arrival_time),
                                  NOW())
           WHEN TIMESTAMPDIFF(SECOND,
               del_info.actual_arrived_to_customer,
               NOW()
               ) > 300
               AND orders.status != 4
               THEN TIMESTAMPDIFF(SECOND, del_info.actual_arrived_to_customer, NOW())
           WHEN orders.processing_type = 'store' AND suppliers.logistic_place_group_id != logistic_place_groups_places.logistic_place_group_id
               THEN NULL
           WHEN ((orders.processing_type = "native" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 1500)
               OR (orders.processing_type = "fast_food" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 2100)
               OR (orders.processing_type = "store" AND TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time) >= 480))
               THEN TIMESTAMPDIFF(SECOND, del_info.planned_arrived_to_place, del_info.max_place_arrival_time)
        END as order_delay_time
FROM bigfood.order_delivery_info AS del_info
    INNER JOIN bigfood.orders AS orders ON orders.id = del_info.order_id
    INNER JOIN bigfood.places AS places ON places.id = orders.place_id
    INNER JOIN bigfood.couriers AS couriers ON couriers.id = orders.courier_id
    INNER JOIN bigfood.suppliers AS suppliers ON couriers.id = suppliers.external_id
    LEFT JOIN bigfood.logistic_place_groups_places AS logistic_place_groups_places ON logistic_place_groups_places.place_id = places.id
    LEFT JOIN bigfood.logistics_ongoing_deliveries_data AS logistics_ongoing_deliveries_data ON logistics_ongoing_deliveries_data.id = del_info.id
    LEFT JOIN bigfood_vendor.order_status_history AS order_status_history ON orders.id = order_status_history.order_id
    LEFT JOIN (
        SELECT DISTINCT origin_id, status
        FROM bigfood.integration_order_statuses
        WHERE updated_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 7200 SECOND)
    ) as integration_order_statuses on integration_order_statuses.origin_id = orders.order_nr
WHERE orders.status IN (1, 2, 3, 6, 7, 9)
    AND del_info.max_place_arrival_time IS NOT NULL
    AND orders.created_at >= DATE_SUB(NOW(), INTERVAL 7200 SECOND)
    AND orders.address_city IN ('Казань')
HAVING {order_delay_type_filter}
AND  order_delay_type IS NOT NULL
;
