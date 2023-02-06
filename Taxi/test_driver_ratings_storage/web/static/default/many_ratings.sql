INSERT INTO driver_ratings_storage.drivers(driver_id, rating, used_scores_num, new_rating_calc_at, details)
VALUES ('driver_id_1', 4.0, 25, '2019-05-01 00:00:00.000000', NULL),
       ('driver_id_2', 4.1, 15, '2019-05-01 00:00:00.000000', '[{"ts": 1599047171.819,"order": "f314d82912803505b0d3f77ba3912e77","rating": 5,"weight": 1}]'::JSONB),
       ('driver_id_3', 4.2, 35, '2019-05-01 00:01:00.000000', '[{"ts": 1599047171.819,"order": "f314d82912803505b0d3f77ba3912e78","rating": 4,"weight": 2}, {"count": 11, "rating": 5, "source": "padding", "artificial": true}]'::JSONB),
       ('driver_id_8', 4.7, 12, '2019-05-01 00:01:01.000000', NULL),
       ('driver_id_9', 4.8, 54, '2019-05-01 00:01:01.000000', NULL),
       ('driver_id_4', 4.3, 45, '2019-05-01 00:02:00.000000', NULL),
       ('driver_id_5', 4.4, 55, '2019-05-01 00:02:00.000000', NULL),
       ('driver_id_6', 4.5, 65, '2019-05-01 00:02:00.000000', NULL),
       ('driver_id_7', 4.6, 7, '2019-05-01 00:02:00.000000', NULL),
       ('driver_id_10', 4.9, 45, '2019-05-02 00:00:00.000000', NULL),
       ('driver_id_11', 4.91, 23, '2019-05-02 00:00:00.000000', NULL),
       ('driver_id_12', 4.92, 12, '2019-05-02 00:00:00.000000', NULL),
       ('driver_id_13', 4.93, 10, '2019-05-02 00:00:00.000000', NULL)
;

INSERT INTO driver_ratings_storage.ratings_history (driver_id, rating, calc_at)
VALUES ('driver_id_1', 4.5, '2019-05-01 00:00:00.000000'),
       ('driver_id_2', 4.6, '2019-05-01 00:00:00.000000'),
       ('driver_id_11', 4.7, '2019-05-02 00:00:00.000000'),
       ('driver_id_1', 3.5, '2019-04-01 00:00:00.000000'),
       ('driver_id_2', 3.6, '2019-04-01 00:00:00.000000'),
       ('driver_id_11', 3.7, '2019-04-02 00:00:00.000000')
;
