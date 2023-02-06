INSERT INTO eats_place_rating.place_rating_info(
    place_id, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at, rating_in_user_rating_count, revision
) VALUES (1, 3.2, 5.0, 4.6, 4.6, 5.0, 3.2, false, '2020-11-24'::DATE, 10, 1),
         (1, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE, 10, 2),
         (2, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-24'::DATE, NULL, 3),
         (2, 3.1, 5.0, 4.6, 0.1, 0, -0.1, true, '2020-11-25'::DATE, 12,4),
         (3, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE, 2, 5),
         (4, 3.1, 5.0, 4.5, -0.1, 0, -0.1, false, '2020-11-24'::DATE, NULL, 6),
         (4, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE, NULL, 7),
         (5, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-23'::DATE, 110, 8),
         (5, 3.1, 5.0, 4.4, -0.1, 0, -0.1, true, '2020-11-24'::DATE, 90, 9),
         (5, 3.1, 5.0, 4.5, 0.1, 0, -0.1, true, '2020-11-25'::DATE, 110, 10),
         (6, 3.1, 5.0, 4.5, 0.1, 0, -0.1, false, '2020-11-25'::DATE, 200, 11),
         (7, 3.1, 5.0, 4.5, 0.1, 0, -0.1, false, '2020-11-25'::DATE, 121, 12),
         (8, 3.1, 5.0, 4.5, 0.1, 0, -0.1, false, '2020-11-25'::DATE, 100, 13);

INSERT INTO eats_place_rating.catalog_storage_sync(place_id, synced_revision, last_sync)
VALUES (1, 2, current_timestamp),
       (2, 3, current_timestamp),
       (4, 2, current_timestamp),
       (5, 8, current_timestamp);

INSERT INTO eats_place_rating.place_type(place_id,brand_slug,business)
VALUES (1,NULL,'restaurant'),
       (2,NULL,'restaurant'),
       (3,NULL,'restaurant'),
       (4,NULL,'restaurant'),
       (5,NULL,'restaurant');

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
) VALUES (3, '100-100', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1001', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1002', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1003', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1004', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1005', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1006', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-1007', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (4, '100-1007', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (2, '100-1007', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (3, '100-4008', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (5, '100-4009', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (6, '100-4009', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (7, '100-4001', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (7, '100-4002', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (7, '100-4003', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (8, '100-4009', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp);

INSERT INTO eats_place_rating.active_places (place_id, updated_at)
VALUES (1, NOW()),
       (2, NOW()),
       (3, NOW()),
       (4, NOW()),
       (5, NOW()),
       (6, NOW()),
       (7, NOW()),
       (8, NOW());
