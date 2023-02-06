INSERT INTO price_modifications.workabilities (rule_id,
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
                                               used_for_perfect_chain)
VALUES
    -- reduce_time_price_by_100
    (1, 'user', 1, false, false, false, true, true, true, true, true, true, true),

    -- paid_supply_addition
    (2, 'driver', 2, false, false, false, true, false, false, false, false, false, false),

    -- half_paid_supply_addition
    (3, 'user', 3, true, false, false, true, true, true, true, true, true, true),

    -- for strikeout price modifications test
    (4, 'user', 4, true, true, false, true, true, true, true, true, true, true),
    (5, 'user', 5, true, true, false, true, true, true, true, true, true, true),
    (6, 'user', 6, true, true, false, false, true, true, true, true, true, true),
    (7, 'user', 7, true, true, false, true, true, true, true, true, true, true)
;
