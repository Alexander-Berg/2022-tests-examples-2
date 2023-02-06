INSERT INTO price_modifications.workabilities (
  rule_id,
  apply_to,
  apply_order,
  used_for_strikeout,
  used_for_total,
  used_for_antisurge,
  used_for_paid_supply,
  used_for_plus_promo,
  used_for_combo_order,
  used_for_combo_inner,
  used_for_combo_outer
)
VALUES
  (1, 'user', 1, true, true, false, false, false, false, true, true),
  (2, 'user', 2, true, true, false, false, false, false, true, true),
  (3, 'user', 3, true, true, false, false, false, false, true, true),
  (2, 'driver', 1, false, true, false, false, false, false, true, true),
  (11, 'driver', 2, false, true, false, false, false, false, true, true)
;
