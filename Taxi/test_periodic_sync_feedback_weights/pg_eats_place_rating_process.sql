INSERT INTO eats_place_rating.feedback_weight
(
    place_id,
    order_nr,
    rating,
    rating_weight,
    feedback_created_at,
    order_created_at,
    calculated_at,
    updated_at
) VALUES (1, '100-100', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-400', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp);

INSERT INTO eats_place_rating.active_places
(
    place_id,
    updated_at
)
VALUES (1, NOW()),
       (2, NOW()),
       (3, NOW());
