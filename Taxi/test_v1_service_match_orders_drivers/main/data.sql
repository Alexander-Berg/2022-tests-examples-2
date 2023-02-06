INSERT INTO formulas.regular(
  da_dist_ratio,
  da_time_ratio,
  home_cancel_prob,
  home_dist_ratio,
  home_time_ratio,
  min_home_dist_ratio,
  min_home_time_ratio,
  min_order_distance,
  min_order_time
) VALUES (
  0.99,
  0.99,
  0.1,
  2.5,
  2.3,
  -0.5,
  -0.5,
  2000,
  300
), (
  0.99,
  0.99,
  0.0,
  3.0,
  3.0,
  -1.0,
  -1.0,
  100,
  100
);

INSERT INTO formulas.regular_offer(
  da_dist_ratio,
  da_time_ratio,
  home_cancel_prob,
  home_dist_ratio,
  home_time_ratio,
  min_home_dist_ratio,
  min_home_time_ratio,
  min_order_distance,
  min_order_time,
  min_b_surge,
  min_surge_gradient
) VALUES (
  0.99,
  0.99,
  0.1,
  2.5,
  2.3,
  -0.5,
  -0.5,
  2000,
  300,
  0.5,
  0.5
), (
  0.99,
  0.99,
  0.0,
  3.0,
  3.0,
  -1.0,
  -1.0,
  100,
  100,
  0.0,
  0.0
);

INSERT INTO formulas.surge(
  min_b_lrsp_time,
  min_b_surge,
  min_order_distance,
  min_order_time
) VALUES (
  300,
  0.5,
  2000,
  300
), (
  100,
  0.0,
  100,
  100
);

INSERT INTO formulas.area SELECT;

INSERT INTO formulas.destination_district(
  max_bh_air_dist,
  max_bh_time,
  dh_time_cmp_coeff
) VALUES (
  5000,
  1800,
  2.4
);

INSERT INTO config.deviation_formulas(
  zone_id,
  mode_id,
  submode_id,
  bonus,
  is_fallback,
  regular_mode,
  regular_offer_mode,
  surge_mode,
  area_mode,
  destination_district_mode
) VALUES (
  1,
  1,
  NULL,
  false,
  false,
  1,
  NULL,
  NULL,
  NULL,
  NULL
), (
  1,
  4,
  NULL,
  false,
  false,
  NULL,
  1,
  NULL,
  NULL,
  NULL
), (
  2,
  4,
  NULL,
  false,
  false,
  NULL,
  NULL,
  1,
  NULL,
  NULL
), (
  1,
  3,
  NULL,
  false,
  false,
  NULL,
  NULL,
  NULL,
  1,
  NULL
), (
  2,
  3,
  NULL,
  false,
  false,
  NULL,
  NULL,
  NULL,
  NULL,
  1
), (
  1,
  1,
  NULL,
  false,
  true,
  2,
  NULL,
  NULL,
  NULL,
  NULL
), (
  1,
  4,
  NULL,
  false,
  true,
  NULL,
  2,
  NULL,
  NULL,
  NULL
), (
  2,
  4,
  NULL,
  false,
  true,
  NULL,
  NULL,
  2,
  NULL,
  NULL
);
