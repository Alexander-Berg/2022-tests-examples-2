INSERT INTO eats_place_rating.place_cancels
(
    place_id,
    order_nr,
    canceled_by_place,
    canceled_by_place_reason,
    calculated_at,
    order_created_at,
    order_finished_at,
    updated_at
) VALUES (1, '100-100', true, 'bad reason', current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-400', false, NULL, current_timestamp, current_timestamp, current_timestamp, current_timestamp);

INSERT INTO eats_place_rating.active_places
(
    place_id,
    updated_at
)
VALUES (1, NOW()),
       (2, NOW()),
       (3, NOW());
