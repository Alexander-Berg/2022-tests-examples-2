-- We need to disable foreign key check to create inconsistent cache state on service start
ALTER TABLE price_modifications.workabilities DISABLE TRIGGER ALL;

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
  (1, 'user', 1, true, true, true, true, true, true, true, true, true, true),
  (42, 'user', 2, true, true, true, true, true, true, true, true, true, true)
;

ALTER TABLE price_modifications.workabilities ENABLE TRIGGER ALL;
