INSERT INTO eats_place_rating.place_cancels_stats
(
    place_id,
    cancel_reason,
    cancel_count,
    calculated_at
)
VALUES (1, 'old reason', 4, current_date),
       (3, 'old reason', 4, current_date);

INSERT INTO eats_place_rating.active_places
(
    place_id,
    updated_at
)
VALUES (1, NOW()),
       (2, NOW()),
       (3, NOW());
