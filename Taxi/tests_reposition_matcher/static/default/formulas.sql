INSERT INTO formulas.regular
(da_dist_ratio, da_time_ratio, home_cancel_prob, home_dist_ratio, home_time_ratio, min_home_dist_ratio, min_home_time_ratio, min_order_distance, min_order_time, sla_params)
VALUES
(1.0,           2.0,           3.0,              4.0,             5.0,             6.0,                 7.0,                 8,                  9, (1, 1, 1, 1, 1)),
(11.0,          12.0,          13.0,             14.0,            15.0,            16.0,                17.0,                18,                 19, NULL),
(21.0,          22.0,          23.0,             24.0,            25.0,            26.0,                27.0,                28,                 29, NULL),
(1.0,           2.0,           3.0,              4.0,             5.0,             6.0,                 7.0,                 8,                  9,  (1, 1, 1, 1, 1)),
(1.0,           2.0,           3.0,              4.0,             5.0,             6.0,                 7.0,                 8,                  9,  (1, 1, 1, 1, 1));

INSERT INTO formulas.regular_offer
(da_dist_ratio, da_time_ratio, home_cancel_prob, home_dist_ratio, home_time_ratio, min_home_dist_ratio, min_home_time_ratio, min_order_distance, min_order_time, min_b_surge, min_surge_gradient, sla_params)
VALUES
(1.0,           2.0,           3.0,              4.0,             5.0,             6.0,                 7.0,                 8,                  9,              10.0,        11.0, NULL),
(11.0,          12.0,          13.0,             14.0,            15.0,            16.0,                17.0,                18,                 19,             110.0,       111.0, (1, 1, 1, 1, 1)),
(21.0,          22.0,          23.0,             24.0,            25.0,            26.0,                27.0,                28,                 29,             210.0,       211.0, NULL),
(11.0,          12.0,          13.0,             14.0,            15.0,            16.0,                17.0,                18,                 19,             110.0,       111.0,  (1, 1, 1, 1, 1));

INSERT INTO formulas.surge
(min_b_lrsp_time, min_b_surge, min_order_distance, min_order_time)
VALUES
(1.0,             2.0,         3.0,                4.0),
(11.0,            12.0,        13.0,               14.0),
(21.0,            22.0,        23.0,               24.0);

INSERT INTO formulas.area SELECT;

INSERT INTO formulas.destination_district
(max_bh_air_dist, max_bh_time, dh_time_cmp_coeff)
VALUES
(1.0,             2.0,         4.0),
(11.0,            12.0,        14.0),
(21.0,            22.0,        24.0);

INSERT INTO config.deviation_formulas
(zone_id, mode_id, submode_id, is_fallback, bonus,       regular_mode, regular_offer_mode, surge_mode, area_mode, destination_district_mode)
VALUES
(1,       1,       NULL,       false,       false,       1,            NULL,               NULL,       NULL,      NULL),
(1,       2,       NULL,       false,       false,       NULL,         1,                  NULL,       NULL,      NULL),
(1,       2,       1,          false,       false,       NULL,         2,                  NULL,       NULL,      NULL),
(1,       2,       1,          false,       true,        4,            NULL,               NULL,       NULL,      NULL),
(1,       2,       2,          false,       true,        NULL,         3,                  NULL,       NULL,      NULL),
(1,       2,       2,          false,       false,       NULL,         4,                  NULL,       NULL,      NULL),
(1,       3,       NULL,       false,       true,        NULL,         NULL,               NULL,       NULL,      1),
(1,       3,       NULL,       false,       false,       NULL,         NULL,               NULL,       1,         NULL),
(1,       3,       4,          false,       false,       NULL,         NULL,               NULL,       NULL,      2),
(1,       3,       3,          false,       true,        NULL,         NULL,               NULL,       NULL,      3),
(1,       3,       3,          false,       false,       5,            NULL,               NULL,       NULL,      NULL),
(1,       4,       NULL,       false,       false,       NULL,         NULL,               1,          NULL,      NULL),
(1,       2,       1,          true,        false,       NULL,         3,                  NULL,       NULL,      NULL),
(1,       2,       1,          true,        true,        1,            NULL,               NULL,       NULL,      NULL);
