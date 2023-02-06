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
  0.5,
  500,
  100
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
  NULL,
  NULL,
  1,
  NULL,
  NULL
), (
  1,
  1,
  NULL,
  true,
  NULL,
  NULL,
  2,
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
