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
  used_for_combo_outer,
  used_for_combo,
  used_for_perfect_chain
)
VALUES
  (1, 'driver', 1, false, true, false, false, false, false, false, false, false, false),
  (1, 'user', 1, false, true, false, false, true, true, true, true, true, true),

  (2, 'driver', 2, false, true, false, false, false, false, false, false, false, false),
  (2, 'user', 2, false, true, false, false, true, true, true, true, true, true),

  (3, 'driver', 3, false, true, false, false, false, false, false, false, false, false),
  (3, 'user', 3, false, true, false, false, true, true, true, true, true, true),

  (5, 'driver', 5, false, true, false, false, false, false, false, false, false, false),
  (5, 'user', 5, false, true, false, false, true, true, true, true, true, true),

  (6, 'driver', 6, false, true, false, false, false, false, false, false, false, false),
  (6, 'user', 6, false, true, false, false, true, true, true, true, true, true),

  (7, 'driver', 7, false, true, false, false, false, false, false, false, false, false),
  (7, 'user', 7, false, true, false, false, true, true, true, true, true, true),

  (8, 'driver', 8, false, true, false, false, false, false, false, false, false, false),
  (8, 'user', 8, false, true, false, false, true, true, true, true, true, true),

  (9, 'driver', 9, true, true, true, true, false, false, false, false, false, false),
  (9, 'user', 9, true, true, true, true, true, true, true, true, true, true),

  (10, 'driver', 10, true, true, true, true, false, false, false, false, false, false),
  (10, 'user', 10, true, true, true, true, true, true, true, true, true, true),

  (11, 'driver', 11, true, true, true, true, false, false, false, false, false, false),
  (11, 'user', 11, true, true, true, true, true, true, true, true, true, true),

  (12, 'driver', 12, true, true, true, true, false, false, false, false, false, false),

  (13, 'user', 12, true, true, true, true, true, true, true, true, true, true),

  (14, 'driver', 13, false, false, true, false, false, false, false, false, false, false),
  (14, 'user', 13, false, false, true, false, true, false, false, false, false, false),

  (15, 'driver', 14, false, true, false, false, false, false, false, false, false, false),
  (15, 'user', 14, false, true, false, false, true, true, true, true, true, true),

  (16, 'driver', 15, false, true, false, true, false, false, false, false, false, false),
  (16, 'user', 15, false, true, false, true, true, true, true, true, true, true),

  (17, 'user', 16, false, false, false, false, false, true, false, false, false, false),
  (18, 'user', 17, true, false, false, false, false, false, true, false, false, false),
  (19, 'user', 18, true, false, false, false, false, false, false, true, false, false),
  (20, 'user', 19, true, false, false, false, false, false, false, false, true, false),
  (21, 'user', 20, true, false, false, false, false, false, false, false, false, true)
;
