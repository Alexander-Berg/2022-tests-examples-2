INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (47, 'waiting', 'Ожидание в точке А', '
let waiting_price = (fix.tariff.transfer_prices as tp) ? tp.waiting_price : fix.tariff.waiting_price;
let paid_waiting_time = ride.ride.waiting_time - waiting_price.free_waiting_time;

if (paid_waiting_time > 0) {
    return {
        waiting = paid_waiting_time *  waiting_price.price_per_minute / 60
    };
}

return ride.price;
', 'both_side', 'ioann-v', 36117, '<AST unneeded>', '2020-01-10 16:58:10.98126+03', NULL, false);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (50, 'paid_supply', 'Платная подача', '
if (fix.category_data.disable_paid_supply as disable_paid_supply) {
    if (fix.category_data.decoupling && disable_paid_supply) {
        return ride.price;
    }
}

if (fix.paid_supply_price as paid_supply_price) {
    return {
        boarding = ride.price.boarding + paid_supply_price
    };
}
return ride.price;
', 'both_side', 'ioann-v', 36124, '<AST unneeded>', '2020-04-08 18:51:07.504417+03', NULL, true);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (99, 'surge', 'Применение суржа', '
if (fix.surge_params.value > 1) {
    let orig_surge = fix.surge_params.value;

    let alpha = (fix.surge_params.surcharge_alpha as s_alpha) ? s_alpha : 1;
    let beta = (fix.surge_params.surcharge_beta as s_beta) ? s_beta : 0;
    let surcharge = (fix.surge_params.surcharge as s_surcharge) ? s_surcharge : 0;

    let alpha_surge_beta = alpha * orig_surge + beta;
    return {
        boarding = alpha_surge_beta * ride.price.boarding + beta * surcharge,
        distance = alpha_surge_beta * ride.price.distance,
        time = alpha_surge_beta * ride.price.time,
        requirements = alpha_surge_beta * ride.price.requirements,
        waiting = orig_surge * ride.price.waiting,
        transit_waiting = orig_surge * ride.price.transit_waiting,
        destnation_waiting = orig_surge * ride.price.destination_waiting
    };
}
return ride.price;
', 'both_side', 'ioann-v', 47448, '<AST unneeded>', '2020-03-27 14:08:22.326137+03', NULL, true);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (141, 'surge', 'Применение суржа', '
if (fix.surge_params.value > 1) {
    let orig_surge = fix.surge_params.value;

    let alpha = (fix.surge_params.surcharge_alpha as s_alpha) ? s_alpha : 1;
    let beta = (fix.surge_params.surcharge_beta as s_beta) ? s_beta : 0;
    let surcharge = (fix.surge_params.surcharge as s_surcharge) ? s_surcharge : 0;

    let alpha_surge_beta = alpha * orig_surge + beta;
    return {
        boarding = alpha_surge_beta * ride.price.boarding + beta * surcharge,
        distance = alpha_surge_beta * ride.price.distance,
        time = alpha_surge_beta * ride.price.time,
        requirements = alpha_surge_beta * ride.price.requirements,
        waiting = orig_surge * ride.price.waiting,
        transit_waiting = orig_surge * ride.price.transit_waiting,
        destnation_waiting = orig_surge * ride.price.destination_waiting
    };
}
return ride.price;
', 'both_side', 'ioann-v', 52235, '<AST unneeded>', '2020-03-27 14:08:22.326137+03', NULL, false);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (143, 'waiting_in_transit', 'Ожидание в пути', '
// Crutch for bad waitings: https://st.yandex-team.ru/EFFICIENCYDEV-12845
if (fix.category == "cargo" || fix.category == "cargocorp") {
  if (ride.ride.waiting_in_transit_time > 82800) { // 82800 seconds is 23 hours
    return ride.price;
  }
}
else {
  if (ride.ride.waiting_in_transit_time > 21600) { // 21600 seconds is 6 hours
    return ride.price;
  }
}

let name = "waiting_in_transit";
let cost_per_second = (name in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[name] / 60 : 0;

let time = ride.ride.waiting_in_transit_time;

if(time > 0) {
    let cost = ride.price.transit_waiting + time * cost_per_second;
    return { transit_waiting = cost, metadata=["waiting_in_transit_delta": round_to(cost, fix.rounding_factor)] };
}

return ride.price;
', 'both_side', 'ioann-v', 52237, '<AST unneeded>', '2020-03-27 14:22:06.904244+03', NULL, false);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (152, 'yaplus', 'Яндекс.Плюс', '
    if (fix.user_data.has_yaplus) {
        if (fix.category_data.yaplus_coeff as coeff) {
            return ride.price * coeff;
        }
    }
    return ride.price;
', 'both_side', 'ioann-v', 53368, '<AST unneeded>', '2020-03-31 19:59:22.421645+03', NULL, false);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (177, 'paid_supply', 'Платная подача', '
if (fix.category_data.disable_paid_supply as disable_paid_supply) {
    if (fix.category_data.decoupling && disable_paid_supply) {
        return ride.price;
    }
}

if (fix.paid_supply_price as paid_supply_price) {
    return {
        boarding = ride.price.boarding + paid_supply_price
    };
}
return ride.price;
', 'both_side', 'ioann-v', 55193, '<AST unneeded>', '2020-04-08 18:51:07.504417+03', NULL, false);


INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (144, 'coupon', 'Применение купона', '
if (fix.coupon as coupon) {
    let meta = {metadata= ["price_before_coupon": *ride.price]};
    if(coupon.percent as percent) {
        if (coupon.limit as limit) {
            let value = ((*ride.price * percent) > limit) ? limit : (*ride.price * percent);
            let price = ride.price * ((*ride.price - value) / *ride.price);
            return concat(meta, price);
        }
        let value = (*ride.price * percent);
        let price = ride.price * ((*ride.price - value) / *ride.price);
        return concat(meta, price);
    }
    let value = coupon.value;
    let price = ride.price * ((*ride.price - value) / *ride.price);
    return concat(meta, price);
}

return ride.price;
', 'both_side', 'ioann-v', 52238, '<AST unneeded>', '2020-03-04 16:16:08.979035+03', NULL, true);

INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted)
    VALUES (200, 'using_trip_distance_and_time', 'Тестовое преобразование', '
return {
    boarding = 200,
    distance = trip.distance,
    time = trip.time,
    requirements = 0,
    waiting = ride.price.boarding,
    transit_waiting = ride.price.distance,
    destination_waiting = ride.price.time
};
', 'both_side', 'ioann-v', 52791, '<AST unneeded>', '2021-08-31 16:20:00.000000+03', NULL, true);

INSERT INTO price_modifications.rules (
    rule_id, name,
    source_code,
    policy, author,
    approvals_id, updated,
    pmv_task_id, deleted, ast
) VALUES (
             95, 'trip_depended',
             'if(fix.quasifixed_params as quasifix){
               let sum = quasifix.distance_a_b +
               10*quasifix.distance_a_bf +
               100*quasifix.distance_b_bf +
               1000*quasifix.distance_bf_b;
               return {distance = sum, metadata=["answer": 42]};
             }
             return ride.price;',
             'both_side', 'me',
             77777, '2020-01-10 18:23:11.5857+03',
             NULL, false, ''
         );
