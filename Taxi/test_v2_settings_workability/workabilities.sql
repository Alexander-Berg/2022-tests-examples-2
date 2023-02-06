INSERT INTO price_modifications.workabilities (
  rule_id,
  scope,
  apply_to,
  apply_order,
  used_for_total,
  used_for_strikeout,
  used_for_antisurge,
  used_for_paid_supply,
  used_for_plus_promo,
  used_for_combo_order,
  used_for_combo_inner,
  used_for_combo_outer,
  used_for_combo,
  used_for_perfect_chain,
  used_for_full_auction
)
VALUES
  (1, 'taxi', 'driver', 1, true, false, true, false, false, false, false, false, false, false, false),
  (2, 'taxi', 'driver', 2, true, false, false, true, false, false, false, false, false, false, false),
  (1, 'taxi', 'user', 1, true, false, true, false, true, true, true, true, true, true, false),
  (3, 'cargo', 'driver', 1, true, false, true, false, false, false, false, false, false, false, false),
  (4, 'cargo', 'user', 2, true, false, false, true, false, false, false, false, false, false, false),
  (5, 'cargo', 'user', 1, true, false, true, false, true, true, true, true, true, true, false)
;
