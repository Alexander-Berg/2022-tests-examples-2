INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    1,
    'emit_price_before_applying_surge',
    '
        // EFFICIENCYDEV-15304
        // Предполагается включение преобразования только на пользователя и только для доп.цен комбо

        return { metadata=["price_before_applying_surge": *ride.price]};
    ',
    'both_side',
    'ivan-popovich',
    1,
    ''
  )
;

INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    2,
    'imitation_surge',
    '
        return ride.price * 1.5;
    ',
    'both_side',
    'ivan-popovich',
    2,
    ''
  )
;

INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    3,
    'user_combo_discount',
    '
        if (fix.combo_offers_data as combo_offers_data){
            if (combo_offers_data.combo_inner_coeff as p) {
                return concat(
                    ride.price * p,
                {metadata = ["combo_discount_absolute_delta": (*ride.price) - (*ride.price) * p]}
                );
            }
        }
        return ride.price;
    ',
    'both_side',
    'ivan-popovich',
    3,
    ''
  )
;

INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    11,
    'driver_combo_discount',
    '
        // EFFICIENCYDEV-15304

        function max(a : double, b : double) {
          return {res = (a > b) ? a : b};
        }

        function min(a : double, b : double) {
          return {res = (a < b) ? a : b};
        }

        let current_price = *ride.price;
        // Ничего не делаем, если цена и так слишком маленькая
        if (current_price < 0.0001) {
          return ride.price;
        }

        // Если на таксометре не поддержана user_meta
        using(UserMeta) {
          // apply_combo_discount_for_driver устанавливается в true в v2/prepare
          // если скидку надо применять к водителю и в false в save_order_details
          // если комбо не сматчилось и надо компенсировать водителю скидку (не включать это преобразование)
            if (fix.combo_offers_data as combo_offers_data){
                if (combo_offers_data.apply_combo_discount_for_driver as apply_combo_discount_for_driver) {
                    if (apply_combo_discount_for_driver) {
                        if ("price_before_applying_surge" in ride.ride.user_meta) {
                            if ("combo_discount_absolute_delta" in ride.ride.user_meta) {
                                let price_before_applying_surge = ride.ride.user_meta["price_before_applying_surge"];
                                let combo_discount_absolute_delta = ride.ride.user_meta["combo_discount_absolute_delta"];
                                // Цена водителя после применения скидки не может стать меньше, чем до применения суржа
                                let price_after_discount = max(a = current_price - combo_discount_absolute_delta, b = price_before_applying_surge).res;
                                // Цена водителя поле применения скидки не должна стать больше изначальной
                                let final_price_after_discount = min(a = price_after_discount, b = current_price).res;

                                let discount_mult = final_price_after_discount / current_price;

                            return ride.price * discount_mult;
                            }
                        }
                    }
                }
            }
        }
        return ride.price;
    ',
    'both_side',
    'ivan-popovich',
    11,
    ''
  )
;
