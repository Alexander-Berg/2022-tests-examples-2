INSERT INTO eats_place_rating.predefined_comments_stats
(
    place_id,
    predefined_comment,
    comments_count,
    comment_type,
    calculated_at
) VALUES (1, 'old comment', 4, 'like', current_date),
         (3, 'old comment', 4, 'like', current_date);

INSERT INTO eats_place_rating.active_places
(
    place_id,
    updated_at
)
VALUES (1, NOW()),
       (2, NOW()),
       (3, NOW());
