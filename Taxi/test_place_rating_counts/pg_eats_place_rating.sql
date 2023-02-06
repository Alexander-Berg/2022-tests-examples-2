INSERT INTO eats_place_rating.place_rating_info(
    place_id, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at
) VALUES (1, 3.1, 3.0, 2.0, -0.1, 0, -0.1, true, '2020-11-25'::DATE),
         (1, 3.2, 3.5, 3.0, 4.6, 5.0, 3.2, false, '2020-11-24'::DATE),
         (1, 3.2, 3.5, 3.1, 4.6, 5.0, 3.2, false, '2020-11-23'::DATE),
         (1, 5, 5, 2.9, 5, 5, 5, true, '2021-03-04'::DATE),
         (3, 4, 4, 4.2, 4, 4, 4, false, '2021-03-04'::DATE),
         (4, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE),
         (5, 3.2, 5.0, 4.6, 4.6, 5.0, 3.2, false, '2021-11-24'::DATE),
         (6, 5, 5, 5, 5, 5, 5, true, '2021-03-04'::DATE);

INSERT INTO eats_place_rating.greenplum_sync(id, last_known_date, last_sync, stats)
VALUES ('greenplum_cursor', (NOW() - interval '1 hour'), NOW(), '{"last_success_import_time": "2021-02-01T21:00:00+0000", "last_known_date": "2021-01-11T00:00:00+0000", "imported_places_num": 20, "new_places_num": 10, "updated_places_num": 10}'::jsonb),
       ('sync-place-cancels-from-greenplum', NOW(), NOW(), '{"imported_objects_num": 123, "places_num_with_objects": 99, "last_sync": "2021-02-01T21:00:00+0000"}'::jsonb),
       ('sync-place-predefined-comments', NOW(), NOW(), '{"imported_objects_num": 111, "places_num_with_objects": 24, "last_sync": "2021-02-01T21:00:00+0000"}'::jsonb),
       ('sync-place-cancels-stats', NOW(), NOW(), '{"imported_objects_num": 7564, "places_num_with_objects": 214, "last_sync": "2021-02-01T21:00:00+0000"}'::jsonb),
       ('sync-feedback-weight-from-greenplum', NOW(), NOW(), '{"imported_objects_num": 8675, "places_num_with_objects": 457, "last_sync": "2021-02-01T21:00:00+0000"}'::jsonb);
