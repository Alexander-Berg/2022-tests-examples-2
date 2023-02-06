SELECT orders.id as `orders_id`,
 orders.order_nr as `orders_order_nr`,
 orders.created_at as `orders_created_at`,
 orders.place_confirmed_at as `orders_place_confirmed_at`,
 orders.type as `orders_type`,
 orders.region_id as `orders_region_id`,
 orders.status as `orders_status`,
 orders.is_asap as `orders_is_asap`,
 orders.call_center_confirmed_at as `orders_call_center_confirmed_at`,
 orders.time_to_delivery_max as `orders_time_to_delivery_max`,
 orders.courier_id as `orders_courier_id`,
 orders.delivered_at as `orders_delivered_at`,
 orders.time_to_delivery as `orders_time_to_delivery`,
 orders.pre_delivery_time as `orders_pre_delivery_time`,
 orders.location_latitude as `orders_location_latitude`,
 orders.location_longitude as `orders_location_longitude`,
 orders.cancelled_at as `orders_cancelled_at`,
 orders.place_id as `orders_place_id`,
 orders.latest_revision_id as `orders_latest_revision_id`,
 orders.flow_type as `orders_flow_type`,
 orders.courier_assigned_at as `orders_courier_assigned_at`,
 places.location_latitude as `places_location_latitude`,
 places.location_longitude as `places_location_longitude`,
 places.enabled as `places_enabled`,
 places.type as `places_type`,
 places.is_fast_food as `places_is_fast_food`,
 places.name as `places_name`,
 places.disable_details_status as `places_disable_details_status`,
 places.address_short as `places_address_short`,
 places.courier_delivery_zone_id as `places_courier_delivery_zone_id`,
 order_cancels.id as `order_cancels_id`,
 order_cancels.reason_id as `order_cancels_reason_id`,
 order_cancel_tasks.reaction_id as `order_cancel_tasks_reaction_id`,
 order_surges.level as `order_surges_level`,
 order_surges.additional_delivery_cost as `order_surges_additional_delivery_cost`,
 order_revisions.id as `order_revisions_id`,
 order_revisions.delivery_date as `order_revisions_delivery_date`,
 order_revisions.items_cost as `order_revisions_items_cost`,
 order_revisions.cost_for_customer as `order_revisions_cost_for_customer`,
 order_revisions.cost_for_place as `order_revisions_cost_for_place`,
 order_revisions.delivery_cost as `order_revisions_delivery_cost`,
 order_cancel_reasons.name as `order_cancel_reasons_name`,
 order_cancel_reasons.group_id as `order_cancel_reasons_group_id`,
 order_cancel_reason_groups.name as `order_cancel_reason_groups_name`,
 regions.name as `regions_name`,
 regions.timezone as `regions_timezone`,
 order_delivery_info.actual_arrived_to_place as `order_delivery_info_actual_arrived_to_place`,
 order_delivery_info.actual_order_taken as `order_delivery_info_actual_order_taken`,
 order_delivery_info.actual_arrived_to_customer as `order_delivery_info_actual_arrived_to_customer`,
 order_delivery_info.max_customer_arrival_time as `order_delivery_info_max_customer_arrival_time`,
 order_delivery_info.max_place_arrival_time as `order_delivery_info_max_place_arrival_time`,
 order_delivery_info.distance_to_customer as `order_delivery_info_distance_to_customer`,
 order_delivery_info.distance_to_place as `order_delivery_info_distance_to_place`,
 order_delivery_info.is_distance_to_customer_precise as `order_delivery_info_is_distance_to_customer_precise`,
 order_delivery_info.is_distance_to_place_precise as `order_delivery_info_is_distance_to_place_precise`,
 couriers.source as `couriers_source`,
 courier_delivery_zones.name as `courier_delivery_zones_name`,
 logistics_taxi_dispatch_requests.reason as `logistics_taxi_dispatch_requests_reason`,
 order_meta_information.meta_information->>'$.delivery_class' as `order_delivery_class`
FROM (
        SELECT id FROM orders
            WHERE orders.created_at >= {start_date} AND orders.created_at <= {end_date} OR
            orders.updated_at >= {start_date} AND orders.updated_at <= {end_date}
        UNION
        SELECT order_surges.order_id AS id FROM order_surges
            WHERE order_surges.created_at >= {start_date} AND order_surges.created_at <= {end_date}
        UNION
        SELECT order_id AS id FROM order_revisions
            WHERE order_revisions.created_at >= {start_date} AND order_revisions.created_at <= {end_date} OR
            order_revisions.updated_at >= {start_date} AND order_revisions.updated_at <= {end_date}
        UNION
        SELECT order_id AS id FROM order_delivery_info
            WHERE order_delivery_info.created_at >= {start_date} AND order_delivery_info.created_at <= {end_date} OR
            order_delivery_info.updated_at >= {start_date} AND order_delivery_info.updated_at <= {end_date}
        UNION
        SELECT order_cancels.order_id AS id FROM order_cancels
            WHERE order_cancels.created_at >= {start_date} AND order_cancels.created_at <= {end_date} OR
            order_cancels.updated_at >= {start_date} AND order_cancels.updated_at <= {end_date}
        UNION
        SELECT order_cancels.order_id AS id FROM order_cancels
            JOIN order_cancel_tasks ON order_cancels.id = order_cancel_tasks.order_cancel_id
            AND (order_cancel_tasks.created_at >= {start_date} AND order_cancel_tasks.created_at <= {end_date} OR
                 order_cancel_tasks.updated_at >= {start_date} AND order_cancel_tasks.updated_at <= {end_date})) as a
INNER JOIN orders on orders.id = a.id
INNER JOIN places ON places.id = orders.place_id
LEFT JOIN order_cancels on order_cancels.order_id = orders.id
LEFT JOIN order_cancel_tasks on order_cancel_tasks.order_cancel_id = order_cancels.id and order_cancel_tasks.reaction_id = 1
LEFT JOIN order_delivery_info ON orders.id = order_delivery_info.order_id
LEFT JOIN order_revisions ON order_revisions.id = orders.latest_revision_id
LEFT JOIN order_cancel_reasons ON order_cancels.reason_id = order_cancel_reasons.id
LEFT JOIN order_cancel_reason_groups ON order_cancel_reasons.group_id = order_cancel_reason_groups.id
LEFT JOIN order_surges ON order_surges.order_id = orders.id
LEFT JOIN regions ON regions.id = orders.region_id
LEFT JOIN couriers ON orders.courier_id = couriers.id
LEFT JOIN courier_delivery_zones ON  places.courier_delivery_zone_id = courier_delivery_zones.id
LEFT JOIN logistics_taxi_dispatch_requests ON orders.order_nr = logistics_taxi_dispatch_requests.order_nr
LEFT JOIN order_meta_information ON orders.order_nr = order_meta_information.order_nr
