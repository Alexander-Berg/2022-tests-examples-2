INSERT INTO eats_place_rating.feedback_weight
(
    place_id,
    order_nr,
    rating,
    rating_weight,
    feedback_created_at,
    order_created_at,
    rating_dt,
    updated_at
) VALUES (1, 'ORDER_1', 5, 201, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (2, 'ORDER_2', 5, 202, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, 'ORDER_3', 5, 203, current_timestamp, current_timestamp, current_timestamp, current_timestamp);
