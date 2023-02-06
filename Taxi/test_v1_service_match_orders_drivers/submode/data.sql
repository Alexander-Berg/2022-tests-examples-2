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
  0.1,
  1.5,
  1.5,
  -0.5,
  -0.5,
  2000,
  300
);

INSERT INTO formulas.area SELECT;

INSERT INTO config.deviation_formulas(
  zone_id,
  mode_id,
  submode_id,
  bonus,
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
  2,
  NULL,
  NULL,
  NULL,
  NULL
), (
  1,
  1,
  2,
  false,
  2,
  NULL,
  NULL,
  NULL,
  NULL
), (
  1,
  1,
  1,
  false,
  1,
  NULL,
  NULL,
  NULL,
  NULL
), (
  1,
  2,
  NULL,
  false,
  NULL,
  NULL,
  NULL,
  1,
  NULL
);
