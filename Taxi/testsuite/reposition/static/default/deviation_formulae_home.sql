INSERT INTO config.deviation_formulae
(
  mode_id,
  zone_id,
  regular_mode
)
VALUES
(
  1,
  1,
  (0.99,0.949,0.1,0.7,0.9,-0.2,-0.1,2120,600)::db.regular_mode
);
