INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1888, 'implicit_discount', 'Неявная скидка (гипербола или таблица)', '
function getMainStrFromExperiment(exp: std::unordered_map<std::string, lang::variables::ExperimentSubValue>) {
  return {str = ("main" in exp) ? (exp["main"].str as str) ? str : " " : " "};
}

function abs(val : double) {
    return {res = (val < 0) ? -val : val};
}

function min(a : double, b : double) {
  return {res = (a < b) ? a : b};
}

function max(a : double, b : double) {
  return {res = (a > b) ? a : b};
}

function minBetweenOptionals(a: std::optional<double>, b_value:double, b_is_set: bool) {
  if (a as a_value) {
    if (b_is_set) {
      return {value=min(a=a_value, b=b_value).res, is_set=true};
    }
    return {value=a_value, is_set=true};
  }
  return {value=b_value, is_set=b_is_set};
}

function calculateHyperbolaDiscountPercent(hyperbolas : clients::discounts::HyperbolasData, price : double) {
    // выбираем гиперболу по порогу
    let hyperbola = (price < hyperbolas.threshold)
        ? hyperbolas.hyperbola_lower
        : hyperbolas.hyperbola_upper;

    // избегаем деления на 0
    if (abs(val=price + hyperbola.c).res < 0.0001) {
        return {res = 0};
    }

    // считаем по формуле гиперболы
    return {res = (hyperbola.p + hyperbola.a / (price + hyperbola.c))};
}

function processTableElement(elem : clients::discounts::TableDataA,
                             has_result: bool,
                             result : double,
                             price : double,
                             first_iteration : bool,
                             prev_elem_price : double,
                             prev_elem_coeff : double) {
    // если результат уже получен, то сразу отдаём его обратно
    if (has_result) {
        return {
            has_result = true,
            result = result,
            // следующие 4 строчки одинаковые во всех return
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // если цена меньше первой цены в таблице, то используем первый элемент
    if (first_iteration && price < elem.price) {
        return {
            has_result = true,
            result = elem.coeff,
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // если цена между предыдущим элементом таблицы и текущим
    if (!first_iteration && prev_elem_price <= price && price < elem.price) {
        // избегаем деления на 0
        if (abs(val=elem.price - prev_elem_price).res < 0.0001) {
            return {
                has_result = true,
                result = 0,
                price = price,
                first_iteration = false,
                prev_elem_price = elem.price,
                prev_elem_coeff = elem.coeff
            };
        }
        // делаем линейную интерполяцию
        return {
            has_result = true,
            result = prev_elem_coeff
                + (elem.coeff - prev_elem_coeff) * (price - prev_elem_price)
                    / (elem.price - prev_elem_price),
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // результат ещё не получен
    return {
        has_result = false,
        result = result,
        price = price,
        first_iteration = false,
        prev_elem_price = elem.price,
        prev_elem_coeff = elem.coeff
    };
}

function calculateTableDiscountPercent(table : std::vector<clients::discounts::TableDataA>, price : double) {
    // проходим по элементам таблицы функцией processTableElement
    let process_table_result = fold(table as elem, processTableElement, {
        has_result = false,
        result = 0,
        price = price,
        first_iteration = true,
        prev_elem_price = 0,
        prev_elem_coeff = 0
    });

    // если результат получен, то отдаём его
    if (process_table_result.has_result) {
        return {res = process_table_result.result};
    }

    // если пришли сюда, то значит цена больше или равна последней цене в таблице, используем последний элемент
    return {res = process_table_result.prev_elem_coeff};
}

function normalizeToMinMax(coeff : double, restrictions : clients::discounts::DiscountRestrictions) {
    // ограничение сверху максимально допустимым значением
    let coeff_limited_to_max = min(a = coeff, b = restrictions.max_discount_coeff).res;
    // если коэффициент меньше минимально допустимого, то сбрасываем в 0 (иначе скидка слишком мелкая)
    return {
        res = (coeff_limited_to_max < restrictions.min_discount_coeff) ? 0 : coeff_limited_to_max
    };
}

function normalizeByMaxAbsoluteValue(coeff : double, price: double, 
                                     max_absolute_value : double) {
    if (price * coeff > max_absolute_value && price > 0.0001) {
        return {
            res = min(a = max(a = max_absolute_value / price, b = 0).res,
                      b = 1).res
        };
    }
    return {res = coeff};
}

function getPreviousCategory() {
  if (fix.category == "business") {
    return {res="econom"};
  } else if (fix.category == "uberselect") {
    return {res="uberx"};
  }
  return {res=" "};
}

// Получаем под экспериментом ограничение максимального значения скидки 
// из значения расчитанного для категории эконом (unberx для uberselect)
// Добавляется в рамках EFFICIENCYDEV-12250
function fetchDiscountRestrictionFromPrevCategory(discount_class: std::string) {
  if ("restrict_absolute_discount" in fix.exps && discount_class == "discounts-calculator") {
    let previous_category = getPreviousCategory().res;
    if (previous_category != " ") {
      let discount_type = getMainStrFromExperiment(exp=fix.exps["restrict_absolute_discount"]).str;
      if (discount_type == "no_discount") {
        return {value=0, is_set=true};
      }
      if (discount_type == "from_previous_category") {
        if (fix.previously_calculated_categories as previously_calculated_categories) {
          if (previous_category in previously_calculated_categories) {
            let econom_meta = previously_calculated_categories[previous_category].user.final_prices["main"].meta;
            if ("discount_delta_raw" in econom_meta) {
              let discount_delta_raw = econom_meta["discount_delta_raw"];
              return {value=-discount_delta_raw, is_set=true};
            }
          }
        }
        // Сюда попадём в том случае, когда не считали предыдущую категорию (например, пересчёт отложки).
        // При этом убираем скидку.
        return {value=0, is_set=true};
      }
    }
  }
  return {value=0, is_set=false};
}


if (fix.discount as discount) {
    // в разницу между между зачёркнутой ценой и обычной
    if (discount.is_price_strikethrough as is_price_strikethrough) {
        if (is_price_strikethrough) {
            return ride.price;
        }
    } else {
      return ride.price;
    }

    let restrictions = discount.restrictions;

    let meta1 = [
      "discount_price": *ride.price  // цена ДО применения скидки, на неподходящее название уже заложился DWH :(
    ];

    // скидка действует на все компоненты цены, кроме ожиданий
    let affected_price = *ride.price - ride.price.waiting
                                     - ride.price.transit_waiting
                                     - ride.price.destination_waiting;

    let percent = (discount.calc_data_hyperbolas as hyp)                                   // если заданы гиперболы
        ? calculateHyperbolaDiscountPercent(hyperbolas = hyp, price = affected_price).res  // считаем скидку по формуле гиперболы
        : (discount.calc_data_table_data as tbl)                                           // если задана таблица
            ? calculateTableDiscountPercent(table = tbl, price = affected_price).res       // считаем скидку по таблице
            : 0;                                                                           // иначе нет скидки

    // Под экспериментом ограничиваем скидку максимальным значением как в экономе
    let discount_class = (discount.discount_class as discount_class) ? discount_class : " ";
    let econom_discount_restriction = fetchDiscountRestrictionFromPrevCategory(discount_class = discount_class);

    let max_absolute_value_opt = minBetweenOptionals(a = restrictions.max_absolute_value,
                                                     b_value = econom_discount_restriction.value,
                                                     b_is_set = econom_discount_restriction.is_set);

    let coeff1 = percent * 0.01;
    let coeff2 = normalizeToMinMax(coeff = coeff1, restrictions = restrictions).res;
    let coeff3 = (max_absolute_value_opt.is_set)
        ? normalizeByMaxAbsoluteValue(coeff = coeff2,
                                      price = affected_price,
                                      max_absolute_value = max_absolute_value_opt.value).res
        : coeff2;
    if (coeff3 <= 0) {
        return {metadata = meta1};
    }
    let coeff_final = min(a = coeff3, b = 1).res;
    let delta = -affected_price * coeff_final;

    let meta2 = [
      // если должна работать как скидка
      "discount_value": coeff_final,
      "discount_delta_raw": delta
    ];

    let mult = 1 - coeff_final;
    return {
        boarding = ride.price.boarding * mult,
        distance = ride.price.distance * mult,
        time = ride.price.time * mult,
        requirements = ride.price.requirements * mult,
        waiting = ride.price.waiting,
        transit_waiting = ride.price.transit_waiting,
        destination_waiting = ride.price.destination_waiting,
        metadata = meta1 + meta2
    };
}

return ride.price;
', 'both_side', 'nfilchenko', 113745, 'FUNC(calcCashbackPrice,ARGS((cashback_rate,double)),B(SV(cashback_price,B(U(*,B(ride,.,F(price))),*,FA(cashback_rate,double)));SV(floor_cashback_price,B(B(fix,.,F(rounding_factor)),*,U(floor,B(VA(cashback_price),/,B(fix,.,F(rounding_factor))))));CR(res=VA(floor_cashback_price))));IF(U(?,B(fix,.,F(payment_type))),SV(high_category,B(B(B(B(B(B(B(fix,.,F(category)),==,"business"),||,B(B(fix,.,F(category)),==,"comfortplus")),||,B(B(fix,.,F(category)),==,"vip")),||,B(B(fix,.,F(category)),==,"ultimate")),||,B(B(fix,.,F(category)),==,"maybach")),||,B(B(fix,.,F(category)),==,"premium_van")));IF(B(B(U(*,B(fix,.,F(payment_type))),==,"corp"),&&,VA(high_category)),IF(B("corp_client_yaplus_cashback",in,B(fix,.,F(exps))),SV(rate,T(B("main",in,B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback")),T(U(?,B(B(B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback"),.,"main"),.,F(val))),U(*,B(B(B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback"),.,"main"),.,F(val))),0.000000),0.000000));SV(price,B(FC(calcCashbackPrice,NT(cashback_rate=VA(rate)),R(res=double)),.,TF(res)));IF(B(B(VA(rate),>,0.000001),&&,B(VA(price),>,0.000001)),E("cashback_rate",VA(rate));E("cashback_discount_fixed_value",VA(price))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-18 16:36:14.729838+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1292, 'base_price_discount', 'EFFICIENCYDEV-10280', '
// Это преобразование может неверно отображаться в детализации: EFFICIENCYDEV-10366

if (fix.base_price_discount as bpd) {
  if (bpd.boarding_discount >= 0 && bpd.boarding_discount <= 1 &&
      bpd.distance_discount >= 0 && bpd.distance_discount <= 1 &&
      bpd.time_discount >= 0 && bpd.time_discount <= 1) {
    return {
      boarding = ride.price.boarding * (1 - bpd.boarding_discount),
      distance = ride.price.distance * (1 - bpd.distance_discount),
      time = ride.price.time * (1 - bpd.time_discount)
    };
  }
}
return ride.price;', 'both_side', 'nfilchenko', 113747, 'IF(U(?,B(fix,.,F(base_price_discount))),IF(B(B(B(B(B(B(B(U(*,B(fix,.,F(base_price_discount))),.,F(boarding_discount)),>=,0.000000),&&,B(B(U(*,B(fix,.,F(base_price_discount))),.,F(boarding_discount)),<=,1.000000)),&&,B(B(U(*,B(fix,.,F(base_price_discount))),.,F(distance_discount)),>=,0.000000)),&&,B(B(U(*,B(fix,.,F(base_price_discount))),.,F(distance_discount)),<=,1.000000)),&&,B(B(U(*,B(fix,.,F(base_price_discount))),.,F(time_discount)),>=,0.000000)),&&,B(B(U(*,B(fix,.,F(base_price_discount))),.,F(time_discount)),<=,1.000000)),CR(boarding=B(B(B(ride,.,F(price)),.,F(boarding)),*,B(1.000000,-,B(U(*,B(fix,.,F(base_price_discount))),.,F(boarding_discount)))),distance=B(B(B(ride,.,F(price)),.,F(distance)),*,B(1.000000,-,B(U(*,B(fix,.,F(base_price_discount))),.,F(distance_discount)))),time=B(B(B(ride,.,F(price)),.,F(time)),*,B(1.000000,-,B(U(*,B(fix,.,F(base_price_discount))),.,F(time_discount)))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-18 16:36:10.177998+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1294, 'paid_cancel_in_driving', 'Несколько вариантов цен отмены в emit', '
if (fix.payment_type as payment_type) {
  if (payment_type == "cash") {
    return ride.price;  // платной отмены за наличные быть не может
  }
}

let paid_supply_disabled = (fix.category_data.disable_paid_supply as disable_paid_supply) ? disable_paid_supply : false;

let paid_supply_paid_cancel = (fix.paid_supply_price as paid_supply_price)
    ? (!paid_supply_disabled && paid_supply_price >= fix.category_data.min_paid_supply_price_for_paid_cancel)
    : false;

if (paid_supply_paid_cancel) {
  if (fix.paid_supply_price as paid_supply_price) {  // этот if разыменовывает уже проверенный выше optional
    return {metadata=["paid_supply_paid_cancel_in_driving_price": round_to(paid_supply_price, fix.rounding_factor)]};
  }
} else if ("driving_paid_cancel" in fix.user_tags) {
  let boarding = fix.tariff.boarding_price;
  return {metadata=["paid_cancel_in_driving_price": round_to(boarding, fix.rounding_factor)]};
}

return ride.price;
', 'both_side', 'nfilchenko', 113749, 'IF(U(?,B(fix,.,F(payment_type))),IF(B(U(*,B(fix,.,F(payment_type))),==,"cash"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));SV(paid_supply_disabled,T(U(?,B(B(fix,.,F(category_data)),.,F(disable_paid_supply))),U(*,B(B(fix,.,F(category_data)),.,F(disable_paid_supply))),false));SV(paid_supply_paid_cancel,T(U(?,B(fix,.,F(paid_supply_price))),B(U(!,VA(paid_supply_disabled)),&&,B(U(*,B(fix,.,F(paid_supply_price))),>=,B(B(fix,.,F(category_data)),.,F(min_paid_supply_price_for_paid_cancel)))),false));IF(VA(paid_supply_paid_cancel),IF(U(?,B(fix,.,F(paid_supply_price))),E("paid_supply_paid_cancel_in_driving_price",B(U(*,B(fix,.,F(paid_supply_price))),round_to,B(fix,.,F(rounding_factor))));IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(good_type,B(B(U(!,VA(corp_type)),&&,U(!,VA(wallet_type))),&&,U(!,VA(corp_acc_type))));IF(B(B(B(B(fix,.,F(user_data)),.,F(has_yaplus)),&&,U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus)))),&&,VA(good_type)),IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),E("paid_supply_paid_cancel_in_driving_price",B(B(U(*,B(fix,.,F(paid_supply_price))),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),round_to,B(fix,.,F(rounding_factor)))))))),IF(B("driving_paid_cancel",in,B(fix,.,F(user_tags))),SV(boarding,B(B(fix,.,F(tariff)),.,F(boarding_price)));E("paid_cancel_in_driving_price",B(VA(boarding),round_to,B(fix,.,F(rounding_factor))));IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(good_type,B(B(U(!,VA(corp_type)),&&,U(!,VA(wallet_type))),&&,U(!,VA(corp_acc_type))));IF(B(B(B(B(fix,.,F(user_data)),.,F(has_yaplus)),&&,U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus)))),&&,VA(good_type)),IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),E("paid_cancel_in_driving_price",B(B(VA(boarding),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),round_to,B(fix,.,F(rounding_factor)))))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-18 16:36:09.776524+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1295, 'prod_requirements_multipliers', 'Требования-мультипликаторы', '
if (fix.tariff.requirement_multipliers as multipliers) {
    with (req_multiplier = 1) generate(req : fix.requirements.select)
        let rname = req.first;
        with (options_multiplier=1) generate(opt: req.second)
            let oname = (opt.independent) ? rname + "." + opt.name : rname;
            let omult = (oname in multipliers) ? multipliers[oname] : 1;
        endgenerate(options_multiplier=options_multiplier * omult)
    endgenerate(req_multiplier = req_multiplier * options_multiplier)

    return ride.price * req_multiplier;
}
return ride.price;
', 'both_side', 'nfilchenko', 113792, 'IF(U(?,B(B(fix,.,F(tariff)),.,F(requirement_multipliers))),GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(select))),I(req_multiplier=1.000000),C(GENERATE(L(opt,B(GV(req),.,F(second))),I(options_multiplier=1.000000),C(),U(options_multiplier=B(GV(options_multiplier),*,T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,U(*,B(B(fix,.,F(tariff)),.,F(requirement_multipliers)))),B(U(*,B(B(fix,.,F(tariff)),.,F(requirement_multipliers))),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),1.000000))))),U(req_multiplier=B(GV(req_multiplier),*,GV(options_multiplier))));CR(boarding=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,GV(req_multiplier)),.,F(waiting))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-18 17:13:32.940884+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1299, 'preorder_multiplier', NULL, 'if (fix.preorder_multiplier as preorder_multiplier) {
  return ride.price * preorder_multiplier;
}
return ride.price;', 'both_side', 'nfilchenko', 113796, 'IF(U(?,B(fix,.,F(preorder_multiplier))),CR(boarding=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,U(*,B(fix,.,F(preorder_multiplier)))),.,F(waiting))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-18 17:13:43.578292+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1305, 'yaplus_corp_for_driver', 'Правило для корпов с яплюсом для водителей', 'if(fix.payment_type as payment_type) {

  let high_category = ( fix.category == "business" || 
                        fix.category == "comfortplus" ||
                        fix.category == "vip" ||
                        fix.category == "ultimate" ||
                        fix.category == "maybach" ||
                        fix.category == "premium_van");

  if (payment_type == "corp" && high_category) {
    if ("corp_client_yaplus_cashback" in fix.exps){
    
      let exp = fix.exps["corp_client_yaplus_cashback"];
      let rate = ("main" in exp) ? (exp["main"].val as val) ? val : 0 : 0;
      
      if (rate > 0.000001){ // корп клиент входит в Эксперимент
        if (fix.category_data.yaplus_coeff as yaplus_coeff) {
          return ride.price * yaplus_coeff;
        }
      }    
    }
  }
}

return ride.price;', 'both_side', 'ioann-v', 116670, 'IF(U(?,B(fix,.,F(payment_type))),SV(high_category,B(B(B(B(B(B(B(fix,.,F(category)),==,"business"),||,B(B(fix,.,F(category)),==,"comfortplus")),||,B(B(fix,.,F(category)),==,"vip")),||,B(B(fix,.,F(category)),==,"ultimate")),||,B(B(fix,.,F(category)),==,"maybach")),||,B(B(fix,.,F(category)),==,"premium_van")));IF(B(B(U(*,B(fix,.,F(payment_type))),==,"corp"),&&,VA(high_category)),IF(B("corp_client_yaplus_cashback",in,B(fix,.,F(exps))),SV(rate,T(B("main",in,B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback")),T(U(?,B(B(B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback"),.,"main"),.,F(val))),U(*,B(B(B(B(fix,.,F(exps)),.,"corp_client_yaplus_cashback"),.,"main"),.,F(val))),0.000000),0.000000));IF(B(VA(rate),>,0.000001),IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),CR(boarding=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(waiting))))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-21 18:27:36.54974+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1309, 'prod_yaplus', 'Яндекс.Плюс', '
if(fix.payment_type as payment_type) {
  let corp_type = payment_type == "corp";
  let wallet_type = payment_type == "personal_wallet";
  let corp_acc_type = payment_type == "coop_account";
  let bad_type = corp_type || wallet_type || corp_acc_type;
  
  if (!fix.user_data.has_yaplus) {
    return ride.price;
  }
  if (bad_type) {
    return ride.price;
  }

  if (fix.category_data.yaplus_coeff as yaplus_coeff) {
    let cashback_for_plus_available = "cashback_for_plus_availability" in fix.exps;
    if (fix.user_data.has_cashback_plus && cashback_for_plus_available) {
      // we will provide cashback instead of discount later in yaplus_cashback
      return ride.price;
    }

    let delta = *ride.price * (1 - yaplus_coeff);

    return concat(ride.price * yaplus_coeff, {metadata=[
      "yaplus_delta_raw": delta,
      "yaplus_delta": round_to(delta, fix.rounding_factor)
    ]});
  }

}

return ride.price;
', 'both_side', 'ioann-v', 118591, 'IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(bad_type,B(B(VA(corp_type),||,VA(wallet_type)),||,VA(corp_acc_type)));IF(U(!,B(B(fix,.,F(user_data)),.,F(has_yaplus))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(VA(bad_type),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),SV(cashback_for_plus_available,B("cashback_for_plus_availability",in,B(fix,.,F(exps))));IF(B(B(B(fix,.,F(user_data)),.,F(has_cashback_plus)),&&,VA(cashback_for_plus_available)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(delta,B(U(*,B(ride,.,F(price))),*,B(1.000000,-,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))))));E("yaplus_delta_raw",VA(delta));E("yaplus_delta",B(VA(delta),round_to,B(fix,.,F(rounding_factor))));CR(boarding=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),.,F(waiting)))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-01-26 13:51:20.456953+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1329, 'emit_details_for_cargo', 'Для детализации логистических заказов', '
// Нужно ставить после requirements_multipliers пока что
if ("cargo_categories_list" in fix.exps && fix.category in fix.exps["cargo_categories_list"]) {
  return {metadata=[
    "base_price.boarding": round_to(ride.price.boarding, fix.rounding_factor),
    "base_price.distance": round_to(ride.price.distance, fix.rounding_factor),
    "base_price.time": round_to(ride.price.time, fix.rounding_factor),
    "base_price": round_to(ride.price.boarding + ride.price.distance + ride.price.time, fix.rounding_factor),

    "waiting_delta": round_to(ride.price.waiting, fix.rounding_factor),
    "waiting_in_destination_delta": round_to(ride.price.destination_waiting, fix.rounding_factor),
    "waiting_in_transit_delta": round_to(ride.price.transit_waiting, fix.rounding_factor)
  ]};
}
return ride.price;

', 'both_side', 'toert', 123271, 'IF(B(B("cargo_categories_list",in,B(fix,.,F(exps))),&&,B(B(fix,.,F(category)),in,B(B(fix,.,F(exps)),.,"cargo_categories_list"))),E("base_price.boarding",B(B(B(ride,.,F(price)),.,F(boarding)),round_to,B(fix,.,F(rounding_factor))));E("base_price.distance",B(B(B(ride,.,F(price)),.,F(distance)),round_to,B(fix,.,F(rounding_factor))));E("base_price.time",B(B(B(ride,.,F(price)),.,F(time)),round_to,B(fix,.,F(rounding_factor))));E("base_price",B(B(B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(distance))),+,B(B(ride,.,F(price)),.,F(time))),round_to,B(fix,.,F(rounding_factor))));E("waiting_delta",B(B(B(ride,.,F(price)),.,F(waiting)),round_to,B(fix,.,F(rounding_factor))));E("waiting_in_destination_delta",B(B(B(ride,.,F(price)),.,F(destination_waiting)),round_to,B(fix,.,F(rounding_factor))));E("waiting_in_transit_delta",B(B(B(ride,.,F(price)),.,F(transit_waiting)),round_to,B(fix,.,F(rounding_factor)))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-02-08 12:25:16.725878+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1423, 'coupon', 'Применение купона', '
// Тесты уже про следующую версию преобразования, но она компилируется по 100 мс :(

if (fix.coupon as coupon) {
  if (coupon.valid) {
    let price = *ride.price;
    let price_before_coupon = round_to(price, fix.rounding_factor);

    let meta1 = [
      "price_before_coupon": price_before_coupon
    ];

    if (price >= 0.0001) {
      if (coupon.percent as percent) {
        let percent_value = price * percent / 100;
        if (coupon.limit as limit) {
          if (limit < percent_value) {
            let result = price - limit;
            let price_after_coupon = (result > 0) ? result : 0;
            let meta2 = [
              "coupon_applying_limit": limit,
              "coupon_value": price_before_coupon - round_to(price_after_coupon, fix.rounding_factor)
            ];
            return concat(ride.price * (price_after_coupon / price), {metadata=meta1 + meta2});
          }
        }
        let result = price - percent_value;
        let price_after_coupon = (result > 0) ? result : 0;
        let meta2 = [
          "coupon_applying_percent": percent,
          "coupon_value": price_before_coupon - round_to(price_after_coupon, fix.rounding_factor)
        ];

        return concat(ride.price * (price_after_coupon / price), {metadata=meta1 + meta2});
      }
      let result = price - coupon.value;
      let price_after_coupon = (result > 0) ? result : 0;
      let coupon_value = price_before_coupon - round_to(price_after_coupon, fix.rounding_factor);
      let meta2 = [
        "coupon_applying_value": coupon_value,
        "coupon_value": coupon_value
      ];
      return concat(ride.price * (price_after_coupon / price), {metadata=meta1 + meta2});
    } else {
      let meta2 = [
        "coupon_value": 0
      ];
      return {metadata=meta1 + meta2};
    }
  }
}

return ride.price;
', 'both_side', 'asaetgaliev', 135064, 'IF(U(?,B(fix,.,F(coupon))),IF(B(U(*,B(fix,.,F(coupon))),.,F(valid)),SV(price,U(*,B(ride,.,F(price))));SV(price_before_coupon,B(VA(price),round_to,B(fix,.,F(rounding_factor))));E("price_before_coupon",VA(price_before_coupon));IF(B(VA(price),>=,0.000100),IF(U(?,B(U(*,B(fix,.,F(coupon))),.,F(percent))),SV(percent_value,B(B(VA(price),*,U(*,B(U(*,B(fix,.,F(coupon))),.,F(percent)))),/,100.000000));IF(U(?,B(U(*,B(fix,.,F(coupon))),.,F(limit))),IF(B(U(*,B(U(*,B(fix,.,F(coupon))),.,F(limit))),<,VA(percent_value)),SV(result,B(VA(price),-,U(*,B(U(*,B(fix,.,F(coupon))),.,F(limit)))));SV(price_after_coupon,T(B(VA(result),>,0.000000),VA(result),0.000000));E("coupon_applying_limit",U(*,B(U(*,B(fix,.,F(coupon))),.,F(limit))));E("coupon_value",B(VA(price_before_coupon),-,B(VA(price_after_coupon),round_to,B(fix,.,F(rounding_factor)))));CR(boarding=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(waiting)))));SV(result,B(VA(price),-,VA(percent_value)));SV(price_after_coupon,T(B(VA(result),>,0.000000),VA(result),0.000000));E("coupon_applying_percent",U(*,B(U(*,B(fix,.,F(coupon))),.,F(percent))));E("coupon_value",B(VA(price_before_coupon),-,B(VA(price_after_coupon),round_to,B(fix,.,F(rounding_factor)))));CR(boarding=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(waiting))));SV(result,B(VA(price),-,B(U(*,B(fix,.,F(coupon))),.,F(value))));SV(price_after_coupon,T(B(VA(result),>,0.000000),VA(result),0.000000));SV(coupon_value,B(VA(price_before_coupon),-,B(VA(price_after_coupon),round_to,B(fix,.,F(rounding_factor)))));E("coupon_applying_value",VA(coupon_value));E("coupon_value",VA(coupon_value));CR(boarding=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,B(VA(price_after_coupon),/,VA(price))),.,F(waiting))),E("coupon_value",0.000000))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-02-26 14:46:08.912329+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1505, 'manual_price_israel', 'Ручной ввод в Израиле', '
// Израиль, Комфорт+
if (fix.country_code2 == "IL" && fix.category == "comfortplus") {
  let suggest_mp = round_to(*ride.price, fix.rounding_factor);
  let meta = [
    "start_manual_price": suggest_mp,
    "min_manual_price": 0,
    "max_manual_price": suggest_mp
  ];


  if ("manual_price" in ride.ride.user_options) {
    let manual_price = ride.ride.user_options["manual_price"] + 0;
    let meta2 = [
      "manual_price": manual_price,
      "manual_price:disp_cost.driver_cost": manual_price,
      "manual_price:disp_cost.taximeter_cost": suggest_mp
    ];

    return {
      boarding = manual_price,
      distance = 0,
      time = 0,
      requirements = 0,
      waiting = 0,
      transit_waiting = 0,
      destination_waiting = 0,
      metadata = meta + meta2
    };
  }
  return { metadata = meta };
}

return ride.price;
', 'both_side', 'ioann-v', 137812, 'IF(B(B(B(fix,.,F(country_code2)),==,"IL"),&&,B(B(fix,.,F(category)),==,"comfortplus")),SV(suggest_mp,B(U(*,B(ride,.,F(price))),round_to,B(fix,.,F(rounding_factor))));E("start_manual_price",VA(suggest_mp));E("min_manual_price",0.000000);E("max_manual_price",VA(suggest_mp));IF(B("manual_price",in,B(B(ride,.,F(ride)),.,F(user_options))),SV(manual_price,B(B(B(ride,.,F(ride)),.,F(user_options)),.,"manual_price"));E("manual_price",VA(manual_price));E("manual_price:disp_cost.driver_cost",VA(manual_price));E("manual_price:disp_cost.taximeter_cost",VA(suggest_mp));CR(boarding=VA(manual_price),destination_waiting=0.000000,distance=0.000000,requirements=0.000000,time=0.000000,transit_waiting=0.000000,waiting=0.000000));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(B(fix,.,F(country_code2)),==,"IL"),&&,B(B(fix,.,F(category)),==,"econom")),IF(B("manual_price",in,B(B(ride,.,F(ride)),.,F(user_options))),SV(manual_price,B(B(B(ride,.,F(ride)),.,F(user_options)),.,"manual_price"));E("manual_price",VA(manual_price));E("manual_price:disp_cost.driver_cost",VA(manual_price));E("manual_price:disp_cost.taximeter_cost",B(U(*,B(ride,.,F(price))),round_to,B(fix,.,F(rounding_factor))));CR(boarding=VA(manual_price),destination_waiting=0.000000,distance=0.000000,requirements=0.000000,time=0.000000,transit_waiting=0.000000,waiting=0.000000));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-04 15:54:34.8234+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1506, 'manual_price_serbia', 'Ручной ввод в Сербии', '
if (fix.country_code2 == "RS") {
  let suggest_mp = round_to(*ride.price, fix.rounding_factor);
  let delta = 10000;
  let meta = [
    "start_manual_price": suggest_mp,
    "min_manual_price": ((suggest_mp > delta) ? suggest_mp - delta : 0),
    "max_manual_price": suggest_mp + delta
  ];

  if ("manual_price" in ride.ride.user_options) {
    let manual_price = ride.ride.user_options["manual_price"] + 0;
    let meta2 = [
        "manual_price": manual_price,
        "manual_price:disp_cost.driver_cost": manual_price,
        "manual_price:disp_cost.taximeter_cost": suggest_mp
      ];
    return {
      boarding = manual_price,
      distance = 0,
      time = 0,
      requirements = 0,
      waiting = 0,
      transit_waiting = 0,
      destination_waiting = 0,
      metadata = meta + meta2
    };
  }
  return {
    metadata = meta
  };
}

return ride.price;', 'both_side', 'ioann-v', 137814, 'IF(B(B(fix,.,F(country_code2)),==,"RS"),SV(suggest_mp,B(U(*,B(ride,.,F(price))),round_to,B(fix,.,F(rounding_factor))));SV(delta,10000.000000);E("start_manual_price",VA(suggest_mp));E("min_manual_price",T(B(VA(suggest_mp),>,VA(delta)),B(VA(suggest_mp),-,VA(delta)),0.000000));E("max_manual_price",B(VA(suggest_mp),+,VA(delta)));IF(B("manual_price",in,B(B(ride,.,F(ride)),.,F(user_options))),SV(manual_price,B(B(B(ride,.,F(ride)),.,F(user_options)),.,"manual_price"));E("manual_price",VA(manual_price));E("manual_price:disp_cost.driver_cost",VA(manual_price));E("manual_price:disp_cost.taximeter_cost",VA(suggest_mp));CR(boarding=VA(manual_price),destination_waiting=0.000000,distance=0.000000,requirements=0.000000,time=0.000000,transit_waiting=0.000000,waiting=0.000000));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-04 15:55:13.779414+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1586, 'requirements', 'Аддитивные требования (кроме hourly_rental)', '
// EFFICIENCYDEV-10241: Для логистики без поддержки "включен один из", иначе безумно долгая компиляция преобразования
if (fix.category == "cargo" || fix.category == "cargocorp" || fix.category == "express" || fix.category == "courier") {
    with (simple_cost = 0, meta1=[]) generate(req : fix.requirements.simple)
        let rprice = (req in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[req] : 0;
        let cmeta = [
          "req:" + req + ":count": 1,
          "req:" + req + ":per_unit": round_to(rprice, fix.rounding_factor),
          "req:" + req + ":price": round_to(rprice, fix.rounding_factor)
        ];
    endgenerate(simple_cost = simple_cost + rprice, meta1 = meta1 + cmeta)

    with (select_cost = 0, meta2 = []) generate(req : fix.requirements.select)
        let rname = req.first;
        with (options_cost = 0, imeta = []) generate(opt : req.second)
            let fullname = rname + "." + opt.name;
            let oname = (opt.independent) ? fullname : rname;
            let ocost = (oname in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[oname] : 0;

            with (opt_count = 0) generate(opt2 : req.second)
            endgenerate(opt_count = opt_count + ((opt.name == opt2.name) ? 1 : 0))
            let cmeta = [
                "req:" + fullname + ":count": opt_count,
                "req:" + fullname + ":per_unit": round_to(ocost, fix.rounding_factor),
                "req:" + fullname + ":price": round_to(opt_count * ocost, fix.rounding_factor)
            ];
        endgenerate(options_cost = options_cost + ocost, imeta = imeta + cmeta)
    endgenerate(select_cost = select_cost + (
        (rname != "hourly_rental")  // почасовая аренда в отдельном преобразовании
            ? options_cost
            : 0
    ), meta2 = meta2 + imeta)

    return {
        requirements = ride.price.requirements + simple_cost + select_cost,
        metadata = meta1 + meta2
    };

// end of EFFICIENCYDEV-10241
} else {

with (simple_cost = 0, meta1=[]) generate(req : fix.requirements.simple)
    let rprice = (req in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[req] : 0;
    let cmeta = [
      "req:" + req + ":count": 1,
      "req:" + req + ":per_unit": round_to(rprice, fix.rounding_factor),
      "req:" + req + ":price": round_to(rprice, fix.rounding_factor)
    ];
endgenerate(simple_cost = simple_cost + rprice, meta1 = meta1 + cmeta)

with (select_cost = 0, meta2 = []) generate(req : fix.requirements.select)
    let rname = req.first;
    with (
        options_cost = 0,
        included_most_expensive = "<none>",
        included_most_expensive_cost = 0,
        meta3 = []
    ) generate(opt : req.second)
        let fullname = rname + "." + opt.name;
        let oname = (opt.independent) ? fullname : rname;
        let ocost = (oname in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[oname] : 0;
        let ocost_if_included = (fix.tariff.requirements_included_one_of as included)
                                    ? (oname in included)
                                          ? ocost
                                          : 0
                                    : 0;

        with (opt_count = 0) generate(opt2 : req.second)
        endgenerate(opt_count = opt_count + ((opt.name == opt2.name) ? 1 : 0))
        let cmeta = [
          "req:" + fullname + ":count": opt_count,
          "req:" + fullname + ":per_unit": round_to(ocost, fix.rounding_factor),
          "req:" + fullname + ":price": round_to(ocost, fix.rounding_factor)  // TODO: если можно, то удалить, иначе как-то исправить, учитывая included
        ];
    endgenerate(
        options_cost = options_cost + ocost,
        included_most_expensive = (ocost_if_included > included_most_expensive_cost)
                                      ? fullname
                                      : included_most_expensive,
        included_most_expensive_cost = (ocost_if_included > included_most_expensive_cost)
                                           ? ocost_if_included
                                           : included_most_expensive_cost,
        meta3 = meta3 + cmeta
    )
    let cmeta = (included_most_expensive != "<none>") ? ["req:" + included_most_expensive + ":included": 1]: [];
endgenerate(select_cost = select_cost + (
    (rname != "hourly_rental")  // почасовая аренда в отдельном преобразовании
        ? options_cost - included_most_expensive_cost
        : 0
), meta2 = meta2 + meta3 + cmeta)

return {
    requirements = ride.price.requirements + simple_cost + select_cost,
    metadata = meta1 + meta2
};

}
', 'both_side', 'ioann-v', 140790, 'IF(B(B(B(B(B(fix,.,F(category)),==,"cargo"),||,B(B(fix,.,F(category)),==,"cargocorp")),||,B(B(fix,.,F(category)),==,"express")),||,B(B(fix,.,F(category)),==,"courier")),GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(simple))),I(simple_cost=0.000000),C(E(B(B("req:",+,GV(req)),+,":count"),1.000000);E(B(B("req:",+,GV(req)),+,":per_unit"),B(T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000),round_to,B(fix,.,F(rounding_factor))));E(B(B("req:",+,GV(req)),+,":price"),B(T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000),round_to,B(fix,.,F(rounding_factor))))),U(simple_cost=B(GV(simple_cost),+,T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000))));GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(select))),I(select_cost=0.000000),C(GENERATE(L(opt,B(GV(req),.,F(second))),I(options_cost=0.000000),C(GENERATE(L(opt2,B(GV(req),.,F(second))),I(opt_count=0.000000),C(),U(opt_count=B(GV(opt_count),+,T(B(B(GV(opt),.,F(name)),==,B(GV(opt2),.,F(name))),1.000000,0.000000))));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":count"),GV(opt_count));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":per_unit"),B(T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),round_to,B(fix,.,F(rounding_factor))));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":price"),B(B(GV(opt_count),*,T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000)),round_to,B(fix,.,F(rounding_factor))))),U(options_cost=B(GV(options_cost),+,T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000))))),U(select_cost=B(GV(select_cost),+,T(B(B(GV(req),.,F(first)),!=,"hourly_rental"),GV(options_cost),0.000000))));CR(requirements=B(B(B(B(ride,.,F(price)),.,F(requirements)),+,GV(simple_cost)),+,GV(select_cost))),GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(simple))),I(simple_cost=0.000000),C(E(B(B("req:",+,GV(req)),+,":count"),1.000000);E(B(B("req:",+,GV(req)),+,":per_unit"),B(T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000),round_to,B(fix,.,F(rounding_factor))));E(B(B("req:",+,GV(req)),+,":price"),B(T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000),round_to,B(fix,.,F(rounding_factor))))),U(simple_cost=B(GV(simple_cost),+,T(B(GV(req),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,GV(req)),0.000000))));GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(select))),I(select_cost=0.000000),C(GENERATE(L(opt,B(GV(req),.,F(second))),I(included_most_expensive="<none>",included_most_expensive_cost=0.000000,options_cost=0.000000),C(GENERATE(L(opt2,B(GV(req),.,F(second))),I(opt_count=0.000000),C(),U(opt_count=B(GV(opt_count),+,T(B(B(GV(opt),.,F(name)),==,B(GV(opt2),.,F(name))),1.000000,0.000000))));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":count"),GV(opt_count));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":per_unit"),B(T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),round_to,B(fix,.,F(rounding_factor))));E(B(B("req:",+,B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name)))),+,":price"),B(T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),round_to,B(fix,.,F(rounding_factor))))),U(included_most_expensive=T(B(T(U(?,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,U(*,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of)))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),0.000000),0.000000),>,GV(included_most_expensive_cost)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),GV(included_most_expensive)),included_most_expensive_cost=T(B(T(U(?,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,U(*,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of)))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),0.000000),0.000000),>,GV(included_most_expensive_cost)),T(U(?,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,U(*,B(B(fix,.,F(tariff)),.,F(requirements_included_one_of)))),T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000),0.000000),0.000000),GV(included_most_expensive_cost)),options_cost=B(GV(options_cost),+,T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F(first)),+,"."),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0.000000))));IF(B(GV(included_most_expensive),!=,"<none>"),E(B(B("req:",+,GV(included_most_expensive)),+,":included"),1.000000))),U(select_cost=B(GV(select_cost),+,T(B(B(GV(req),.,F(first)),!=,"hourly_rental"),B(GV(options_cost),-,GV(included_most_expensive_cost)),0.000000))));CR(requirements=B(B(B(B(ride,.,F(price)),.,F(requirements)),+,GV(simple_cost)),+,GV(select_cost))))', '2021-03-12 18:23:29.572111+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1588, 'marketing_cashback_logistics', 'Маркетинговый кэшбек в логистике', '
function getAvailableCashback() {
  if ("marketing_cashback_logistics" in fix.exps) {
      let rate = ("main" in fix.exps["marketing_cashback_logistics"])
          ? (fix.exps["marketing_cashback_logistics"]["main"].val as val) ? val : 0
          : 0;
      return {enabled=true, rate=rate};
  }
  return {enabled=false, rate=0.0};
}

function calcCashbackPrice(cashback_rate: double) {
  let cashback_price = *ride.price * cashback_rate;
  let round_cashback_price = round_to(cashback_price, fix.rounding_factor);
  return {res = round_cashback_price};
}

// только если юзер не тратит ранее накопленный кешбек
if (fix.complements as complements) {
  return ride.price;
}

// только в России
if (fix.country_code2 != "RU") {
  return ride.price;
}

// только на тарифы логистики
if (fix.category != "express" &&
    fix.category != "courier" &&
    fix.category != "cargo") {
  return ride.price;
}

// только кешбечным плюсовикам
if (!fix.user_data.has_yaplus || !fix.user_data.has_cashback_plus) {
    return ride.price;
}

// только имеющим тег 
if (!("logistics_plus_exp_frequent_user" in fix.user_tags)) {
    return ride.price;
}

// только на card, applepay, googlepay
if (fix.payment_type as payment_type) {
  if (payment_type != "card" &&
      payment_type != "applepay" &&
      payment_type != "googlepay") {
    return ride.price;
  }
}

// проверяем, доступен ли пользователю кэшбек  и получаем процент кэшбека
let cashback_params = getAvailableCashback();
if (cashback_params.enabled) {
  let rate = cashback_params.rate;
  let price = calcCashbackPrice(cashback_rate=rate).res;
  let meta = [
    "marketing_cashback_logistics_rate": rate
  ];
  if (rate > 0.000001 && price > 0.000001) {  // эпсилон-окрестность;
    let meta2 = [
      "cashback_rate": rate,
      "cashback_discount_fixed_value": price
    ];
    return {metadata=meta + meta2};
  }
  return {metadata=meta};
}

return ride.price;

', 'both_side', 'aliev-r', 145600, 'FUNC(calcCashbackPrice,ARGS((cashback_rate,double)),B(SV(cashback_price,B(U(*,B(ride,.,F(price))),*,FA(cashback_rate,double)));SV(round_cashback_price,B(VA(cashback_price),round_to,B(fix,.,F(rounding_factor))));CR(res=VA(round_cashback_price))));FUNC(getAvailableCashback,ARGS(),B(IF(B("marketing_cashback_logistics",in,B(fix,.,F(exps))),SV(rate,T(B("main",in,B(B(fix,.,F(exps)),.,"marketing_cashback_logistics")),T(U(?,B(B(B(B(fix,.,F(exps)),.,"marketing_cashback_logistics"),.,"main"),.,F(val))),U(*,B(B(B(B(fix,.,F(exps)),.,"marketing_cashback_logistics"),.,"main"),.,F(val))),0.000000),0.000000));CR(enabled=true,rate=VA(rate)));CR(enabled=false,rate=0.000000)));IF(U(?,B(fix,.,F(complements))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(fix,.,F(country_code2)),!=,"RU"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(B(B(fix,.,F(category)),!=,"express"),&&,B(B(fix,.,F(category)),!=,"courier")),&&,B(B(fix,.,F(category)),!=,"cargo")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(U(!,B(B(fix,.,F(user_data)),.,F(has_yaplus))),||,U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus)))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(!,B("logistics_plus_exp_frequent_user",in,B(fix,.,F(user_tags)))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(payment_type))),IF(B(B(B(U(*,B(fix,.,F(payment_type))),!=,"card"),&&,B(U(*,B(fix,.,F(payment_type))),!=,"applepay")),&&,B(U(*,B(fix,.,F(payment_type))),!=,"googlepay")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(FC(getAvailableCashback,NT(),R(enabled=bool,rate=double)),.,TF(enabled)),SV(rate,B(FC(getAvailableCashback,NT(),R(enabled=bool,rate=double)),.,TF(rate)));SV(price,B(FC(calcCashbackPrice,NT(cashback_rate=VA(rate)),R(res=double)),.,TF(res)));IF(B(B(VA(rate),>,0.000001),&&,B(VA(price),>,0.000001)),E("cashback_rate",VA(rate));E("cashback_discount_fixed_value",VA(price)));E("marketing_cashback_logistics_rate",VA(rate)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-25 12:29:09.999307+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1593, 'personal_wallet', 'Применение персонального кошелька', '
function getMinimalPrimaryPayment() {
  let minimal_primary_sum_exp = "composite_payment_minimal_primary_sum" in fix.exps;
  if (!minimal_primary_sum_exp) {
      return {res = 0};
  }

  return {res = fix.rounding_factor};
}

function max(a : double, b : double) {
  return {res = (a > b) ? a : b};
}


if (fix.complements as complements) {
  if (complements.personal_wallet as personal_wallet) {
    let min_primary_payment = getMinimalPrimaryPayment().res;

    let display_price = (*ride.price > personal_wallet.balance)
        ? (*ride.price - personal_wallet.balance)
        : 0;
    
    let display_price_rounded = round_to(display_price, fix.rounding_factor);

    let display_min_price = (fix.tariff.minimum_price > personal_wallet.balance)
        ? (fix.tariff.minimum_price - personal_wallet.balance)
        : 0;

    let display_min_price_rounded = round_to(display_min_price, fix.rounding_factor);

    return {metadata=[
      "display_price": max(a = display_price_rounded, b = min_primary_payment).res,
      "display_min_price": display_min_price_rounded
    ]};
  }
}

return ride.price;', 'both_side', 'danielkono', 142837, 'FUNC(getMinimalPrimaryPayment,ARGS(),B(SV(minimal_primary_sum_exp,B("composite_payment_minimal_primary_sum",in,B(fix,.,F(exps))));IF(U(!,VA(minimal_primary_sum_exp)),CR(res=0.000000));CR(res=B(fix,.,F(rounding_factor)))));FUNC(max,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),>,FA(b,double)),FA(a,double),FA(b,double)))));IF(U(?,B(fix,.,F(complements))),IF(U(?,B(U(*,B(fix,.,F(complements))),.,F(personal_wallet))),SV(min_primary_payment,B(FC(getMinimalPrimaryPayment,NT(),R(res=double)),.,TF(res)));SV(display_price,T(B(U(*,B(ride,.,F(price))),>,B(U(*,B(U(*,B(fix,.,F(complements))),.,F(personal_wallet))),.,F(balance))),B(U(*,B(ride,.,F(price))),-,B(U(*,B(U(*,B(fix,.,F(complements))),.,F(personal_wallet))),.,F(balance))),0.000000));SV(display_price_rounded,B(VA(display_price),round_to,B(fix,.,F(rounding_factor))));E("display_price",B(FC(max,NT(a=VA(display_price_rounded),b=VA(min_primary_payment)),R(res=double)),.,TF(res)));SV(display_min_price,T(B(B(B(fix,.,F(tariff)),.,F(minimum_price)),>,B(U(*,B(U(*,B(fix,.,F(complements))),.,F(personal_wallet))),.,F(balance))),B(B(B(fix,.,F(tariff)),.,F(minimum_price)),-,B(U(*,B(U(*,B(fix,.,F(complements))),.,F(personal_wallet))),.,F(balance))),0.000000));SV(display_min_price_rounded,B(VA(display_min_price),round_to,B(fix,.,F(rounding_factor))));E("display_min_price",VA(display_min_price_rounded))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-18 13:35:47.047335+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1604, 'paid_cancel_in_waiting', 'Расчёт платной отмены в waiting', '
let waiting_time = (ride.ride.waiting_time < fix.category_data.paid_cancel_waiting_time_limit)
                        ? ride.ride.waiting_time
                        : fix.category_data.paid_cancel_waiting_time_limit;


let price_per_minute = (fix.tariff.transfer_prices as transfer_prices)
                          ? transfer_prices.waiting_price.price_per_minute
                          : fix.tariff.waiting_price.price_per_minute;
let waiting_price = waiting_time * price_per_minute / 60;

let minimal_cancel_price = (fix.tariff.paid_cancel_options as options)
                                ? (  options.paid_cancel_fix
                                   + ((options.add_minimal_to_paid_cancel) ? fix.tariff.boarding_price : 0))
                                : 0;
let paid_cancel_in_waiting_price = minimal_cancel_price + waiting_price;

return {metadata=[
  "paid_cancel_in_waiting_paid_time": waiting_time, // for debug only
  "paid_cancel_in_waiting_price": round_to(paid_cancel_in_waiting_price, fix.rounding_factor)
]};
'
, 'both_side', 'a-andriyanov', 144940, 'SV(waiting_time,T(B(B(B(ride,.,F(ride)),.,F(waiting_time)),<,B(B(fix,.,F(category_data)),.,F(paid_cancel_waiting_time_limit))),B(B(ride,.,F(ride)),.,F(waiting_time)),B(B(fix,.,F(category_data)),.,F(paid_cancel_waiting_time_limit))));E("paid_cancel_in_waiting_paid_time",VA(waiting_time));SV(price_per_minute,T(U(?,B(B(fix,.,F(tariff)),.,F(transfer_prices))),B(B(U(*,B(B(fix,.,F(tariff)),.,F(transfer_prices))),.,F(waiting_price)),.,F(price_per_minute)),B(B(B(fix,.,F(tariff)),.,F(waiting_price)),.,F(price_per_minute))));SV(waiting_price,B(B(VA(waiting_time),*,VA(price_per_minute)),/,60.000000));SV(minimal_cancel_price,T(U(?,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),B(B(U(*,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),.,F(paid_cancel_fix)),+,T(B(U(*,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),.,F(add_minimal_to_paid_cancel)),B(B(fix,.,F(tariff)),.,F(boarding_price)),0.000000)),0.000000));SV(paid_cancel_in_waiting_price,B(VA(minimal_cancel_price),+,VA(waiting_price)));E("paid_cancel_in_waiting_price",B(VA(paid_cancel_in_waiting_price),round_to,B(fix,.,F(rounding_factor))));IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(good_type,B(B(U(!,VA(corp_type)),&&,U(!,VA(wallet_type))),&&,U(!,VA(corp_acc_type))));IF(B(B(B(B(fix,.,F(user_data)),.,F(has_yaplus)),&&,U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus)))),&&,VA(good_type)),IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),E("paid_cancel_in_waiting_price",B(B(VA(paid_cancel_in_waiting_price),*,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff)))),round_to,B(fix,.,F(rounding_factor)))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-24 06:01:18.642108+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1609, 'marketing_cashback_econom', 'Маркетинговый кэшбек на Экономе', '
function getNewPlusDistributionFlow() {
  // эксперимент-рубильник
  let exp_enabled = "marketing_cashback_econom" in fix.exps;
  if (!exp_enabled) {
    return {enabled=false, control=false, rate=0.0};
  }

  // дистрибуция работает только на неплюсовиков и свежих плюсовиков
  if (fix.user_data.has_yaplus && "active_plusers_for_filtering" in fix.user_tags) {
    return {enabled=false, control=false, rate=0.0};
  }

  // находится ли юзер в одной из контрольных групп
  let econom_no_plus_control = "econom_no_plus_control" in fix.user_tags;
  let econom_no_plus_comm_control = "econom_no_plus_comm_control" in fix.user_tags;
  let control = econom_no_plus_control || econom_no_plus_comm_control;

  let cashback_type_available = (fix.payment_type as payment_type)
      ? (payment_type == "card" || payment_type == "applepay" || payment_type == "googlepay")
          ? "cashless"
          : (payment_type == "cash") ? "cash" : "disabled"
      : "disabled";
  
  let exp = fix.exps["marketing_cashback_econom"];
  if (cashback_type_available != "disabled") {
      let rate = (cashback_type_available in exp) ? (exp[cashback_type_available].val as val) ? val : 0 : 0;
      return {enabled=true, control=control, rate=rate};
  } else {
      return {enabled=false, control=false, rate=0.0};
  }
}

function getStairwayCashback(user_tags: std::unordered_set<std::string>) {
  if ("cashback_for_econom_percent_0" in fix.user_tags) {
    return {enabled=true, rate=0.0};
  }
  if ("cashback_for_econom_percent_1" in fix.user_tags) {
    return {enabled=true, rate=0.01};
  }
  if ("cashback_for_econom_percent_2" in fix.user_tags) {
    return {enabled=true, rate=0.02};
  }
  if ("cashback_for_econom_percent_3" in fix.user_tags) {
    return {enabled=true, rate=0.03};
  }
  if ("cashback_for_econom_percent_4" in fix.user_tags) {
    return {enabled=true, rate=0.04};
  }
  if ("cashback_for_econom_percent_5" in fix.user_tags) {
    return {enabled=true, rate=0.05};
  }
  if ("cashback_for_econom_percent_6" in fix.user_tags) {
    return {enabled=true, rate=0.06};
  }
  if ("cashback_for_econom_percent_7" in fix.user_tags) {
    return {enabled=true, rate=0.07};
  }
  if ("cashback_for_econom_percent_8" in fix.user_tags) {
    return {enabled=true, rate=0.08};
  }
  if ("cashback_for_econom_percent_9" in fix.user_tags) {
    return {enabled=true, rate=0.09};
  }
  if ("cashback_for_econom_percent_10" in fix.user_tags) {
    return {enabled=true, rate=0.1};
  }
  return {enabled=false, rate=0.0};
}

function calcCashbackPrice(cashback_rate: double) {
  let cashback_price = *ride.price * cashback_rate;
  let round_cashback_price = round_to(cashback_price, fix.rounding_factor);
  return {res = round_cashback_price};
}

// нет кэшбека, когда часть поездки оплачивается накопленным кэшбеком
if (fix.complements as complements) {
  return ride.price;
}

// нет кэшбека вне России и не на Экономе
if (fix.country_code2 != "RU" || fix.category != "econom") {
  return ride.price;
}

if (fix.payment_type as payment_type) {
  // нет кэшбека, когда тип оплаты отличается от card, applepay, googlepay и + наличные
  if (payment_type != "card" &&
    payment_type != "applepay" &&
    payment_type != "googlepay" && 
    payment_type != "cash") {
    return ride.price;
  }

  // привлекаем неплюсовиков
  let new_distribution_flow = getNewPlusDistributionFlow();
  if (new_distribution_flow.enabled) {
      // юзер в контрольной группе - нет кешбека
      if (new_distribution_flow.control) {
        return {
          metadata=["marketing_cashback_econom_control": 1]
        };
      }
      let rate = new_distribution_flow.rate;
      let price = calcCashbackPrice(cashback_rate=rate).res;
      if (rate > 0.000001 && price > 0.000001) {  // эпсилон-окрестность
        return { metadata=[
          "marketing_cashback_econom_rate": rate,
          "cashback_rate": rate,
          "cashback_discount_fixed_value": price
        ]};
      }
  // идем по старому флоу с кешбеком лесенкой плюсовикам и только на карту
  } else if (fix.user_data.has_yaplus && payment_type != "cash") {
    let cashback_stairway_exp_enabled = "cashback_stairway_to_econom" in fix.exps;
    let stairway_cashback = getStairwayCashback(user_tags=fix.user_tags);
    // если есть кешбек от лесенки - выдаем
    if (cashback_stairway_exp_enabled && stairway_cashback.enabled) {
      let rate = stairway_cashback.rate;
      let price = calcCashbackPrice(cashback_rate=rate).res;
      if (rate > 0.000001 && price > 0.000001) {  // эпсилон-окрестность
        return { metadata=[
          "stairway_cashback_rate": rate,
          "cashback_rate": rate,
          "cashback_discount_fixed_value": price
        ]};
      }
    }
  }
}

return ride.price;
', 'both_side', 'aliev-r', 145602, 'FUNC(calcCashbackPrice,ARGS((cashback_rate,double)),B(SV(cashback_price,B(U(*,B(ride,.,F(price))),*,FA(cashback_rate,double)));SV(round_cashback_price,B(VA(cashback_price),round_to,B(fix,.,F(rounding_factor))));CR(res=VA(round_cashback_price))));FUNC(getNewPlusDistributionFlow,ARGS(),B(SV(exp_enabled,B("marketing_cashback_econom",in,B(fix,.,F(exps))));IF(U(!,VA(exp_enabled)),CR(control=false,enabled=false,rate=0.000000));IF(B(B(B(fix,.,F(user_data)),.,F(has_yaplus)),&&,B("active_plusers_for_filtering",in,B(fix,.,F(user_tags)))),CR(control=false,enabled=false,rate=0.000000));SV(econom_no_plus_control,B("econom_no_plus_control",in,B(fix,.,F(user_tags))));SV(econom_no_plus_comm_control,B("econom_no_plus_comm_control",in,B(fix,.,F(user_tags))));SV(control,B(VA(econom_no_plus_control),||,VA(econom_no_plus_comm_control)));IF(B(T(U(?,B(fix,.,F(payment_type))),T(B(B(B(U(*,B(fix,.,F(payment_type))),==,"card"),||,B(U(*,B(fix,.,F(payment_type))),==,"applepay")),||,B(U(*,B(fix,.,F(payment_type))),==,"googlepay")),"cashless",T(B(U(*,B(fix,.,F(payment_type))),==,"cash"),"cash","disabled")),"disabled"),!=,"disabled"),SV(rate,T(B(T(U(?,B(fix,.,F(payment_type))),T(B(B(B(U(*,B(fix,.,F(payment_type))),==,"card"),||,B(U(*,B(fix,.,F(payment_type))),==,"applepay")),||,B(U(*,B(fix,.,F(payment_type))),==,"googlepay")),"cashless",T(B(U(*,B(fix,.,F(payment_type))),==,"cash"),"cash","disabled")),"disabled"),in,B(B(fix,.,F(exps)),.,"marketing_cashback_econom")),T(U(?,B(B(B(B(fix,.,F(exps)),.,"marketing_cashback_econom"),.,T(U(?,B(fix,.,F(payment_type))),T(B(B(B(U(*,B(fix,.,F(payment_type))),==,"card"),||,B(U(*,B(fix,.,F(payment_type))),==,"applepay")),||,B(U(*,B(fix,.,F(payment_type))),==,"googlepay")),"cashless",T(B(U(*,B(fix,.,F(payment_type))),==,"cash"),"cash","disabled")),"disabled")),.,F(val))),U(*,B(B(B(B(fix,.,F(exps)),.,"marketing_cashback_econom"),.,T(U(?,B(fix,.,F(payment_type))),T(B(B(B(U(*,B(fix,.,F(payment_type))),==,"card"),||,B(U(*,B(fix,.,F(payment_type))),==,"applepay")),||,B(U(*,B(fix,.,F(payment_type))),==,"googlepay")),"cashless",T(B(U(*,B(fix,.,F(payment_type))),==,"cash"),"cash","disabled")),"disabled")),.,F(val))),0.000000),0.000000));CR(control=VA(control),enabled=true,rate=VA(rate)),CR(control=false,enabled=false,rate=0.000000))));FUNC(getStairwayCashback,ARGS((user_tags,std::unordered_set<std::string>)),B(IF(B("cashback_for_econom_percent_0",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.000000));IF(B("cashback_for_econom_percent_1",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.010000));IF(B("cashback_for_econom_percent_2",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.020000));IF(B("cashback_for_econom_percent_3",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.030000));IF(B("cashback_for_econom_percent_4",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.040000));IF(B("cashback_for_econom_percent_5",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.050000));IF(B("cashback_for_econom_percent_6",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.060000));IF(B("cashback_for_econom_percent_7",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.070000));IF(B("cashback_for_econom_percent_8",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.080000));IF(B("cashback_for_econom_percent_9",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.090000));IF(B("cashback_for_econom_percent_10",in,B(fix,.,F(user_tags))),CR(enabled=true,rate=0.100000));CR(enabled=false,rate=0.000000)));IF(U(?,B(fix,.,F(complements))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(B(fix,.,F(country_code2)),!=,"RU"),||,B(B(fix,.,F(category)),!=,"econom")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(payment_type))),IF(B(B(B(B(U(*,B(fix,.,F(payment_type))),!=,"card"),&&,B(U(*,B(fix,.,F(payment_type))),!=,"applepay")),&&,B(U(*,B(fix,.,F(payment_type))),!=,"googlepay")),&&,B(U(*,B(fix,.,F(payment_type))),!=,"cash")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(FC(getNewPlusDistributionFlow,NT(),R(control=bool,enabled=bool,rate=double)),.,TF(enabled)),IF(B(FC(getNewPlusDistributionFlow,NT(),R(control=bool,enabled=bool,rate=double)),.,TF(control)),E("marketing_cashback_econom_control",1.000000);CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(rate,B(FC(getNewPlusDistributionFlow,NT(),R(control=bool,enabled=bool,rate=double)),.,TF(rate)));SV(price,B(FC(calcCashbackPrice,NT(cashback_rate=VA(rate)),R(res=double)),.,TF(res)));IF(B(B(VA(rate),>,0.000001),&&,B(VA(price),>,0.000001)),E("marketing_cashback_econom_rate",VA(rate));E("cashback_rate",VA(rate));E("cashback_discount_fixed_value",VA(price))),IF(B(B(B(fix,.,F(user_data)),.,F(has_yaplus)),&&,B(U(*,B(fix,.,F(payment_type))),!=,"cash")),SV(cashback_stairway_exp_enabled,B("cashback_stairway_to_econom",in,B(fix,.,F(exps))));IF(B(VA(cashback_stairway_exp_enabled),&&,B(FC(getStairwayCashback,NT(user_tags=B(fix,.,F(user_tags))),R(enabled=bool,rate=double)),.,TF(enabled))),SV(rate,B(FC(getStairwayCashback,NT(user_tags=B(fix,.,F(user_tags))),R(enabled=bool,rate=double)),.,TF(rate)));SV(price,B(FC(calcCashbackPrice,NT(cashback_rate=VA(rate)),R(res=double)),.,TF(res)));IF(B(B(VA(rate),>,0.000001),&&,B(VA(price),>,0.000001)),E("stairway_cashback_rate",VA(rate));E("cashback_rate",VA(rate));E("cashback_discount_fixed_value",VA(price)))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-03-25 12:30:14.659289+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1638, 'callcenter', 'Использование коэффициентов колл-центра', '// TAXIBACKEND-34773
if (fix.category == "vezeteconom" || fix.category == "vezetcomfort") {
  return ride.price;
}

// Флаг decoupling сейчас может быть выставлен только в данных у пользователя (не у водителя)
if (fix.category_data.decoupling) {
  return ride.price;
}

let extra = (fix.category_data.callcenter_extra_percents as p) ? 1 + p / 100 : 1;
let discount = (fix.category_data.callcenter_discount_percents as p) ? 1 - p / 100 : 1;
let k = extra * discount;

return ride.price * k;', 'both_side', 'ioann-v', 147670, 'IF(B(B(B(fix,.,F(category)),==,"vezeteconom"),||,B(B(fix,.,F(category)),==,"vezetcomfort")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(fix,.,F(category_data)),.,F(decoupling)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(extra,T(U(?,B(B(fix,.,F(category_data)),.,F(callcenter_extra_percents))),B(1.000000,+,B(U(*,B(B(fix,.,F(category_data)),.,F(callcenter_extra_percents))),/,100.000000)),1.000000));SV(discount,T(U(?,B(B(fix,.,F(category_data)),.,F(callcenter_discount_percents))),B(1.000000,-,B(U(*,B(B(fix,.,F(category_data)),.,F(callcenter_discount_percents))),/,100.000000)),1.000000));SV(k,B(VA(extra),*,VA(discount)));CR(boarding=B(B(B(ride,.,F(price)),*,VA(k)),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,VA(k)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,VA(k)),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,VA(k)),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,VA(k)),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,VA(k)),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,VA(k)),.,F(waiting)))', '2021-03-30 20:21:14.005979+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1651, 'emit_gepard_price_details', NULL, '
let free_waiting_time = (fix.tariff.transfer_prices as transfer_prices)
                          ? transfer_prices.waiting_price.free_waiting_time
                          : fix.tariff.waiting_price.free_waiting_time;

return {metadata=[
  "gepard_min_price_raw": ride.price.boarding + ride.price.requirements,
  "gepard_waiting_price_raw": ride.price.waiting,
  "gepard_waiting_in_transit_price_raw": ride.price.transit_waiting,
  "gepard_waiting_in_destination_price_raw": ride.price.destination_waiting,
  "gepard_base_price_raw": ride.price.boarding + ride.price.distance + ride.price.time,
  "gepard_free_waiting_minutes": round_to(free_waiting_time / 60, 0.001),
  "gepard_paid_waiting_minutes": round_to(ride.ride.waiting_time / 60, 0.001)
]};
', 'both_side', 'artmbogatov', 149335, 'E("gepard_min_price_raw",B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(requirements))));E("gepard_waiting_price_raw",B(B(ride,.,F(price)),.,F(waiting)));E("gepard_waiting_in_transit_price_raw",B(B(ride,.,F(price)),.,F(transit_waiting)));E("gepard_waiting_in_destination_price_raw",B(B(ride,.,F(price)),.,F(destination_waiting)));E("gepard_base_price_raw",B(B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(distance))),+,B(B(ride,.,F(price)),.,F(time))));SV(free_waiting_time,T(U(?,B(B(fix,.,F(tariff)),.,F(transfer_prices))),B(B(U(*,B(B(fix,.,F(tariff)),.,F(transfer_prices))),.,F(waiting_price)),.,F(free_waiting_time)),B(B(B(fix,.,F(tariff)),.,F(waiting_price)),.,F(free_waiting_time))));E("gepard_free_waiting_minutes",B(B(VA(free_waiting_time),/,60.000000),round_to,0.001000));E("gepard_paid_waiting_minutes",B(B(B(B(ride,.,F(ride)),.,F(waiting_time)),/,60.000000),round_to,0.001000));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-04-02 16:13:18.059169+03', NULL, false, '{gepard_min_price_raw,gepard_waiting_price_raw,gepard_waiting_in_transit_price_raw,gepard_waiting_in_destination_price_raw,gepard_base_price_raw,gepard_free_waiting_minutes,gepard_paid_waiting_minutes}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1709, 'corp_driver_price_coeff_israel', 'Повышение водительской стоимости для корпоративных поездок Израиля', '// CORPDEV-1993
if (fix.payment_type as payment_type) {
  if (payment_type == "corp" && fix.country_code2 == "IL") {
    let corp_driver_price_coeff_israel_exp = "corp_driver_price_coeff_israel";
    if (corp_driver_price_coeff_israel_exp in fix.exps) {
      let exp = fix.exps[corp_driver_price_coeff_israel_exp];
      let coeff = ("main" in exp) ? ((exp["main"].val as val) ? val : 1) : 1;
      return ride.price * coeff;
    }
  }
}
return ride.price;', 'both_side', 'igor-bond', 156286, 'IF(U(?,B(fix,.,F(payment_type))),IF(B(B(U(*,B(fix,.,F(payment_type))),==,"corp"),&&,B(B(fix,.,F(country_code2)),==,"IL")),IF(B("corp_driver_price_coeff_israel",in,B(fix,.,F(exps))),SV(coeff,T(B("main",in,B(B(fix,.,F(exps)),.,"corp_driver_price_coeff_israel")),T(U(?,B(B(B(B(fix,.,F(exps)),.,"corp_driver_price_coeff_israel"),.,"main"),.,F(val))),U(*,B(B(B(B(fix,.,F(exps)),.,"corp_driver_price_coeff_israel"),.,"main"),.,F(val))),1.000000),1.000000));CR(boarding=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,VA(coeff)),.,F(waiting))))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-04-16 18:37:13.984302+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1742, 'cargo_paid_cancel_price', 'Эмит цены платной отмены для NewBiz', '
let waiting_time_limit = fix.category_data.paid_cancel_waiting_time_limit;

let limited_waiting_price = (ride.ride.waiting_time > waiting_time_limit)
                            ? ride.price.waiting * waiting_time_limit / ride.ride.waiting_time
                            : ride.price.waiting;

let base_cancel_price = (fix.tariff.paid_cancel_options as paid_cancel_options)?
  paid_cancel_options.paid_cancel_fix : 0;
let add_minimal_to_paid_cancel = (fix.tariff.paid_cancel_options as paid_cancel_options)?
  paid_cancel_options.add_minimal_to_paid_cancel : true;
let coef_for_minimal = (add_minimal_to_paid_cancel) ? 1 : 0;

let cancel_price_wo_waiting = base_cancel_price + coef_for_minimal * ride.price.boarding;

return {
  metadata=[
    "paid_cancel_price": round_to(cancel_price_wo_waiting + limited_waiting_price, fix.rounding_factor)
  ]
};
', 'both_side', 'ioann-v', 158289, 'SV(waiting_time_limit,B(B(fix,.,F(category_data)),.,F(paid_cancel_waiting_time_limit)));SV(limited_waiting_price,T(B(B(B(ride,.,F(ride)),.,F(waiting_time)),>,VA(waiting_time_limit)),B(B(B(B(ride,.,F(price)),.,F(waiting)),*,VA(waiting_time_limit)),/,B(B(ride,.,F(ride)),.,F(waiting_time))),B(B(ride,.,F(price)),.,F(waiting))));SV(base_cancel_price,T(U(?,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),B(U(*,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),.,F(paid_cancel_fix)),0.000000));SV(add_minimal_to_paid_cancel,T(U(?,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),B(U(*,B(B(fix,.,F(tariff)),.,F(paid_cancel_options))),.,F(add_minimal_to_paid_cancel)),true));SV(coef_for_minimal,T(VA(add_minimal_to_paid_cancel),1.000000,0.000000));SV(cancel_price_wo_waiting,B(VA(base_cancel_price),+,B(VA(coef_for_minimal),*,B(B(ride,.,F(price)),.,F(boarding)))));E("paid_cancel_price",B(B(VA(cancel_price_wo_waiting),+,VA(limited_waiting_price)),round_to,B(fix,.,F(rounding_factor))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-04-21 17:59:28.955001+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1792, 'increase_to_minimum_price_taximeter', 'Повысить цену до минимальной по тарифу по счётчику', '
function max(a:double, b:double) {
  return { res = (a > b) ? a : b };
}

// Коэффициент максимально разрешённого тарифа
let mrt_coeff = (fix.base_price_discount as bpd) ? bpd.boarding_discount : 1;

// Минимальная цена = [максимум из посадки и минимальной цены в тарифе] * [коэффициент МРТ]
let minimum = max(a=fix.tariff.boarding_price, b=fix.tariff.minimum_price).res * mrt_coeff;

let delta = (ride.price.boarding + ride.price.distance + ride.price.time < minimum)
              ? minimum - (ride.price.boarding + ride.price.distance + ride.price.time)
              : 0;

return {
  boarding = ride.price.boarding + delta,
  metadata=[
    "increase_to_minimum_price_delta_raw": delta,
    "increase_to_minimum_price_delta": round_to(delta, fix.rounding_factor)
  ]
};
', 'taximeter_only', 'ioann-v', 162357, 'FUNC(max,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),>,FA(b,double)),FA(a,double),FA(b,double)))));SV(mrt_coeff,T(U(?,B(fix,.,F(base_price_discount))),B(U(*,B(fix,.,F(base_price_discount))),.,F(boarding_discount)),1.000000));SV(minimum,B(B(FC(max,NT(a=B(B(fix,.,F(tariff)),.,F(boarding_price)),b=B(B(fix,.,F(tariff)),.,F(minimum_price))),R(res=double)),.,TF(res)),*,VA(mrt_coeff)));SV(delta,T(B(B(B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(distance))),+,B(B(ride,.,F(price)),.,F(time))),<,VA(minimum)),B(VA(minimum),-,B(B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(distance))),+,B(B(ride,.,F(price)),.,F(time)))),0.000000));E("increase_to_minimum_price_delta_raw",VA(delta));E("increase_to_minimum_price_delta",B(VA(delta),round_to,B(fix,.,F(rounding_factor))));CR(boarding=B(B(B(ride,.,F(price)),.,F(boarding)),+,VA(delta)))', '2021-04-29 20:02:36.736829+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1842, 'waiting_in_destination', 'Ожидание в точке Б (разгрузка)', '
// Crutch for bad waitings: https://st.yandex-team.ru/EFFICIENCYDEV-12845
if (fix.category == "cargo" || fix.category == "cargocorp") {
  if (ride.ride.waiting_in_destination_time > 82800) { // 82800 seconds is 23 hours
    return ride.price;
  }
}
else {
  if (ride.ride.waiting_in_destination_time > 21600) { // 21600 seconds is 6 hours
    return ride.price;
  }
}

let name = "unloading";
let cost_per_second = (name in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[name] / 60 : 0;

let time = ride.ride.waiting_in_destination_time;

if(time > 0) {
    let cost = ride.price.destination_waiting + time * cost_per_second;
    return { destination_waiting = cost,
             metadata=[
                "waiting_in_destination_delta": round_to(cost, fix.rounding_factor)
             ]
    };
}

return ride.price;
', 'both_side', 'ivan-popovich', 169772, 'IF(B(B(B(fix,.,F(category)),==,"cargo"),||,B(B(fix,.,F(category)),==,"cargocorp")),IF(B(B(B(ride,.,F(ride)),.,F(waiting_in_destination_time)),>,82800.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))),IF(B(B(B(ride,.,F(ride)),.,F(waiting_in_destination_time)),>,21600.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));SV(cost_per_second,T(B("unloading",in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,"unloading"),/,60.000000),0.000000));SV(time,B(B(ride,.,F(ride)),.,F(waiting_in_destination_time)));IF(B(VA(time),>,0.000000),SV(cost,B(B(B(ride,.,F(price)),.,F(destination_waiting)),+,B(VA(time),*,VA(cost_per_second))));E("waiting_in_destination_delta",B(VA(cost),round_to,B(fix,.,F(rounding_factor))));CR(destination_waiting=VA(cost)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-20 16:50:24.877779+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1843, 'prod_waiting', NULL, '
// Crutch for bad waitings: https://st.yandex-team.ru/EFFICIENCYDEV-12845
if (fix.category == "cargo" || fix.category == "cargocorp") {
  if (ride.ride.waiting_time > 82800) { // 82800 seconds is 23 hours
    return ride.price;
  }
}
else {
  if (ride.ride.waiting_time > 21600) { // 21600 seconds is 6 hours
    return ride.price;
  }
}

if (ride.ride.waiting_time > 0) {
  let price_per_minute = (fix.tariff.transfer_prices as transfer_prices)
                          ? transfer_prices.waiting_price.price_per_minute
                          : fix.tariff.waiting_price.price_per_minute;
  let waiting_price = ride.ride.waiting_time * price_per_minute / 60;
  return {waiting = waiting_price,
          metadata=[
            "waiting_delta": round_to(waiting_price, fix.rounding_factor),
            "waiting_delta_raw": waiting_price
          ]
  };
}

return ride.price;
', 'both_side', 'ivan-popovich', 169774, 'IF(B(B(B(fix,.,F(category)),==,"cargo"),||,B(B(fix,.,F(category)),==,"cargocorp")),IF(B(B(B(ride,.,F(ride)),.,F(waiting_time)),>,82800.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))),IF(B(B(B(ride,.,F(ride)),.,F(waiting_time)),>,21600.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(B(B(ride,.,F(ride)),.,F(waiting_time)),>,0.000000),SV(price_per_minute,T(U(?,B(B(fix,.,F(tariff)),.,F(transfer_prices))),B(B(U(*,B(B(fix,.,F(tariff)),.,F(transfer_prices))),.,F(waiting_price)),.,F(price_per_minute)),B(B(B(fix,.,F(tariff)),.,F(waiting_price)),.,F(price_per_minute))));SV(waiting_price,B(B(B(B(ride,.,F(ride)),.,F(waiting_time)),*,VA(price_per_minute)),/,60.000000));E("waiting_delta",B(VA(waiting_price),round_to,B(fix,.,F(rounding_factor))));E("waiting_delta_raw",VA(waiting_price));CR(waiting=VA(waiting_price)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-20 16:51:13.246583+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1844, 'prod_waiting_in_transit', 'Ожидание в пути', '
// Crutch for bad waitings: https://st.yandex-team.ru/EFFICIENCYDEV-12845
if (fix.category == "cargo" || fix.category == "cargocorp") {
  if (ride.ride.waiting_in_transit_time > 82800) { // 82800 seconds is 23 hours
    return ride.price;
  }
}
else {
  if (ride.ride.waiting_in_transit_time > 43200) { // 43200 seconds is 12 hours
    return ride.price;
  }
}

let name = "waiting_in_transit";
let cost_per_second = (name in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[name] / 60 : 0;

let time = ride.ride.waiting_in_transit_time;

if(time > 0) {
    let cost = ride.price.transit_waiting + time * cost_per_second;
    return { transit_waiting = cost,
             metadata=[
              "waiting_in_transit_delta": round_to(cost, fix.rounding_factor)
             ]
    };
}

return ride.price;
', 'both_side', 'ivan-popovich', 169780, 'IF(B(B(B(fix,.,F(category)),==,"cargo"),||,B(B(fix,.,F(category)),==,"cargocorp")),IF(B(B(B(ride,.,F(ride)),.,F(waiting_in_transit_time)),>,82800.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))),IF(B(B(B(ride,.,F(ride)),.,F(waiting_in_transit_time)),>,21600.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));SV(cost_per_second,T(B("waiting_in_transit",in,B(B(fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(B(fix,.,F(tariff)),.,F(requirement_prices)),.,"waiting_in_transit"),/,60.000000),0.000000));SV(time,B(B(ride,.,F(ride)),.,F(waiting_in_transit_time)));IF(B(VA(time),>,0.000000),SV(cost,B(B(B(ride,.,F(price)),.,F(transit_waiting)),+,B(VA(time),*,VA(cost_per_second))));E("waiting_in_transit_delta",B(VA(cost),round_to,B(fix,.,F(rounding_factor))));CR(transit_waiting=VA(cost)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-20 16:56:15.284039+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1869, 'emit_components', 'Эмитит округлённые цены посадки и за ожидания', '
function max(a:double, b:double) {
  return { res = (a > b) ? a : b };
}

// Минимальная цена = [максимум из посадки + требований и минимальной цены в тарифе]
let minimum_price = max(a=(ride.price.boarding + ride.price.requirements), b=fix.tariff.minimum_price).res;

return { metadata=[
  "min_price": round_to(minimum_price, fix.rounding_factor),
  "waiting_price": round_to(ride.price.waiting, fix.rounding_factor),
  "waiting_in_transit_price": round_to(ride.price.transit_waiting, fix.rounding_factor),
  "waiting_in_destination_price": round_to(ride.price.destination_waiting, fix.rounding_factor)
]};
', 'both_side', 'alexeybykov', 173051, 'FUNC(max,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),>,FA(b,double)),FA(a,double),FA(b,double)))));SV(minimum_price,B(FC(max,NT(a=B(B(B(ride,.,F(price)),.,F(boarding)),+,B(B(ride,.,F(price)),.,F(requirements))),b=B(B(fix,.,F(tariff)),.,F(minimum_price))),R(res=double)),.,TF(res)));E("min_price",B(VA(minimum_price),round_to,B(fix,.,F(rounding_factor))));E("waiting_price",B(B(B(ride,.,F(price)),.,F(waiting)),round_to,B(fix,.,F(rounding_factor))));E("waiting_in_transit_price",B(B(B(ride,.,F(price)),.,F(transit_waiting)),round_to,B(fix,.,F(rounding_factor))));E("waiting_in_destination_price",B(B(B(ride,.,F(price)),.,F(destination_waiting)),round_to,B(fix,.,F(rounding_factor))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-26 15:17:17.200666+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1874, 'prod_surge', 'Применение суржа', '
function getMainStringFromExperiment(exp: std::unordered_map<std::string, lang::variables::ExperimentSubValue>) {
  return {str = ("main" in exp) ? (exp["main"].str as str) ? str : " " : " "};
}

function getToValueFromExperiment(exp: std::unordered_map<std::string, lang::variables::ExperimentSubValue>) {
  return {val = ("to" in exp) ? (exp["to"].val as val) ? val : 0.001 : 0.001};
}

function makeSetcarMetaRounded(effective_surge : double, is_cargo_category: bool) {
  if ("setcar_show_surge_or_surcharge" in fix.exps) {
    let show_surge_or_surcharge = getMainStringFromExperiment(exp=fix.exps["setcar_show_surge_or_surcharge"]).str;

    let fact_surge = (*ride.price > 0.0001)
        ? (*ride.price + effective_surge) / *ride.price
        : 1.0;
    let round_fact_surge = round_to((fact_surge - 0.05), 0.1);
    let round_delta = round_to(effective_surge, fix.rounding_factor);

    if (show_surge_or_surcharge == "show_surge" && round_fact_surge > 1.0001  && !is_cargo_category) {
      return { meta = [
        "setcar.show_surge": round_fact_surge
      ] };
    } else if ((is_cargo_category || show_surge_or_surcharge == "show_surcharge") && effective_surge > 0.0001) {
      return { meta = [
        "setcar.show_surcharge": round_delta
      ] };
    }
  }
  return { meta = [] };
}

function makeSetcarMeta(is_cargo_category: bool, price_after_surge: double, delta: double) {
  if ("setcar_show_surge_or_surcharge" in fix.exps) {
    let show_surge_or_surcharge = getMainStringFromExperiment(exp=fix.exps["setcar_show_surge_or_surcharge"]).str;

    let fact_surge = (*ride.price > 0.0001)
        ? price_after_surge / *ride.price
        : 1.0;
    let round_fact_surge = round_to((fact_surge - 0.05), 0.1);
    let round_delta = round_to(delta, fix.rounding_factor);

    if (show_surge_or_surcharge == "show_surge" && round_fact_surge > 1.0001 && !is_cargo_category) {
      return { meta = [
        "setcar.show_surge": round_fact_surge
      ] };
    } else if ((is_cargo_category || show_surge_or_surcharge == "show_surcharge") && round_delta > 0.0001) {
      return { meta = [
        "setcar.show_surcharge": round_delta
      ] };
    }
  }
  return { meta = [] };
}

// Отключаем сурж для заказов Синтегро
if (fix.zone == "boryasvo") {
  return ride.price;
}

let DEFAULT_ALPHA = 1;
let DEFAULT_BETA = 0;
let DEFAULT_SURCHARGE = 0;

let orig_surge = fix.surge_params.value;

let alpha = (orig_surge >= 1) ? ((fix.surge_params.surcharge_alpha as s_alpha) ? s_alpha : DEFAULT_ALPHA) : DEFAULT_ALPHA;
let beta = (orig_surge >= 1) ? ((fix.surge_params.surcharge_beta as s_beta) ? s_beta : DEFAULT_BETA) : DEFAULT_BETA;
let surcharge = (orig_surge >= 1) ? ((fix.surge_params.surcharge as s_surcharge) ? s_surcharge : DEFAULT_SURCHARGE) : DEFAULT_SURCHARGE;

// surge < 1 - это неявный антисурж, его на преобразованиях не делаем
let surge = (orig_surge >= 1) ? orig_surge : 1;

let alpha_surge_beta = alpha * surge + beta;

let is_cargo_category = "cargo_categories_list" in fix.exps && fix.category in fix.exps["cargo_categories_list"];
let waitings_coeff = (fix.country_code2 == "RU" && !is_cargo_category) ? surge : 1;

let waiting = waitings_coeff * ride.price.waiting;
let transit_waiting = waitings_coeff * ride.price.transit_waiting;
let destination_waiting = waitings_coeff * ride.price.destination_waiting;

// Если уже что-то пообещали на фикс-прайсе, то это и используем (требует дублирование категории в CATEGORIES_CALCULATION_ORDER)
if (fix.previously_calculated_categories as pcc) {
  if (fix.category in pcc) {
    let meta = pcc[fix.category].driver.final_prices["main"].meta;  // Используем метаданные водителя

    if ("setcar.show_surge" in meta) {
        let coeff = meta["setcar.show_surge"];

        let surge_delta_raw = coeff * (ride.price.boarding + ride.price.distance + ride.price.time + ride.price.requirements)
            + waiting + transit_waiting + destination_waiting - *ride.price;

        return {
            boarding = coeff * ride.price.boarding,
            distance = coeff * ride.price.distance,
            time = coeff * ride.price.time,
            requirements = coeff * ride.price.requirements,
            waiting = waiting,
            transit_waiting = transit_waiting,
            destination_waiting = destination_waiting,
            metadata = [
              "surge_delta_raw": surge_delta_raw,
              "surge_delta": round_to(surge_delta_raw, fix.rounding_factor)
            ]
        };
    }

    if ("setcar.show_surcharge" in meta) {
        let addition = meta["setcar.show_surcharge"];

        let surge_delta_raw = addition
            + waiting - ride.price.waiting
            + transit_waiting - ride.price.transit_waiting
            + destination_waiting - ride.price.destination_waiting;

        return {
            boarding = ride.price.boarding + addition,
            waiting = waiting,
            transit_waiting = transit_waiting,
            destination_waiting = destination_waiting,
            metadata = [
              "surge_delta_raw": surge_delta_raw,
              "surge_delta": round_to(surge_delta_raw, fix.rounding_factor)
            ]
        };
    }
  }
}

let boarding = alpha_surge_beta * ride.price.boarding + beta * surcharge;
let distance = alpha_surge_beta * ride.price.distance;
let time = alpha_surge_beta * ride.price.time;
let requirements = alpha_surge_beta * ride.price.requirements;

// В расчетах дельты нужно использовать только составляющие boarding, distance, time, requirements
let price_after_surge = boarding
    + distance
    + time
    + requirements
    + ride.price.waiting
    + ride.price.transit_waiting
    + ride.price.destination_waiting;
let delta = price_after_surge - *ride.price;

// Округлённый сурж
if ("surge_rounding" in fix.exps) {
  let surge_rounding_factor = getToValueFromExperiment(exp=fix.exps["surge_rounding"]).val;
  let effective_surge = round_to(delta, surge_rounding_factor);

  let meta1 = makeSetcarMetaRounded(effective_surge=effective_surge, is_cargo_category=is_cargo_category).meta;

  let surge_delta_raw = ride.price.boarding + effective_surge
      + ride.price.distance
      + ride.price.time
      + ride.price.requirements
      + waiting
      + transit_waiting
      + destination_waiting
      - *ride.price;

  let meta2 = [
    "surge_delta_raw": surge_delta_raw,  // not rounded
    "surge_delta": round_to(surge_delta_raw, fix.rounding_factor)
  ];

  return {
    boarding = ride.price.boarding + effective_surge,
    waiting = waiting,
    transit_waiting = transit_waiting,
    destination_waiting = destination_waiting,
    metadata = meta1 + meta2
  };
}

let meta1 = makeSetcarMeta(price_after_surge=price_after_surge, is_cargo_category=is_cargo_category, delta=delta).meta;

let surge_delta_raw = boarding
    + distance
    + time
    + requirements
    + waiting
    + transit_waiting
    + destination_waiting
    - *ride.price;

let meta2 = [
  "surge_delta_raw": surge_delta_raw,  // not rounded
  "surge_delta": round_to(surge_delta_raw, fix.rounding_factor)
];

return {
  boarding = boarding,
  distance = distance,
  time = time,
  requirements = requirements,
  waiting = waiting,
  transit_waiting = transit_waiting,
  destination_waiting = destination_waiting,
  metadata = meta1 + meta2
};', 'taximeter_only', 'a-andriyanov', 173146, 'FUNC(getMainStringFromExperiment,ARGS((exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),B(CR(str=T(B("main",in,FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),T(U(?,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(str))),U(*,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(str)))," ")," "))));FUNC(getToValueFromExperiment,ARGS((exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),B(CR(val=T(B("to",in,FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),T(U(?,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"to"),.,F(val))),U(*,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"to"),.,F(val))),0.001000),0.001000))));IF(U(?,B(fix,.,F(discount))),IF(B(B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(recalc_type)),==,lang::variables::RecalcType::kBasicPrice),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(B(fix,.,F(zone)),==,"boryasvo"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(DEFAULT_ALPHA,1.000000);SV(DEFAULT_BETA,0.000000);SV(DEFAULT_SURCHARGE,0.000000);SV(orig_surge,B(B(fix,.,F(surge_params)),.,F(value)));SV(alpha,T(B(VA(orig_surge),>=,1.000000),T(U(?,B(B(fix,.,F(surge_params)),.,F(surcharge_alpha))),U(*,B(B(fix,.,F(surge_params)),.,F(surcharge_alpha))),VA(DEFAULT_ALPHA)),VA(DEFAULT_ALPHA)));SV(beta,T(B(VA(orig_surge),>=,1.000000),T(U(?,B(B(fix,.,F(surge_params)),.,F(surcharge_beta))),U(*,B(B(fix,.,F(surge_params)),.,F(surcharge_beta))),VA(DEFAULT_BETA)),VA(DEFAULT_BETA)));SV(surcharge,T(B(VA(orig_surge),>=,1.000000),T(U(?,B(B(fix,.,F(surge_params)),.,F(surcharge))),U(*,B(B(fix,.,F(surge_params)),.,F(surcharge))),VA(DEFAULT_SURCHARGE)),VA(DEFAULT_SURCHARGE)));SV(surge,T(B(VA(orig_surge),>=,1.000000),VA(orig_surge),1.000000));SV(alpha_surge_beta,B(B(VA(alpha),*,VA(surge)),+,VA(beta)));SV(is_cargo_category,B(B("cargo_categories_list",in,B(fix,.,F(exps))),&&,B(B(fix,.,F(category)),in,B(B(fix,.,F(exps)),.,"cargo_categories_list"))));SV(waitings_coeff,T(B(B(B(fix,.,F(country_code2)),==,"RU"),&&,U(!,VA(is_cargo_category))),VA(surge),1.000000));SV(boarding,B(B(VA(alpha_surge_beta),*,B(B(ride,.,F(price)),.,F(boarding))),+,B(VA(beta),*,VA(surcharge))));SV(distance,B(VA(alpha_surge_beta),*,B(B(ride,.,F(price)),.,F(distance))));SV(time,B(VA(alpha_surge_beta),*,B(B(ride,.,F(price)),.,F(time))));SV(requirements,B(VA(alpha_surge_beta),*,B(B(ride,.,F(price)),.,F(requirements))));SV(waiting,B(VA(waitings_coeff),*,B(B(ride,.,F(price)),.,F(waiting))));SV(transit_waiting,B(VA(waitings_coeff),*,B(B(ride,.,F(price)),.,F(transit_waiting))));SV(destination_waiting,B(VA(waitings_coeff),*,B(B(ride,.,F(price)),.,F(destination_waiting))));SV(price_after_surge,B(B(B(B(B(B(VA(boarding),+,VA(distance)),+,VA(time)),+,VA(requirements)),+,B(B(ride,.,F(price)),.,F(waiting))),+,B(B(ride,.,F(price)),.,F(transit_waiting))),+,B(B(ride,.,F(price)),.,F(destination_waiting))));SV(delta,B(VA(price_after_surge),-,U(*,B(ride,.,F(price)))));IF(B("surge_rounding",in,B(fix,.,F(exps))),SV(surge_rounding_factor,B(FC(getToValueFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"surge_rounding")),R(val=double)),.,TF(val)));SV(effective_surge,B(VA(delta),round_to,VA(surge_rounding_factor)));IF(B("setcar_show_surge_or_surcharge",in,B(fix,.,F(exps))),SV(fact_surge,T(B(U(*,B(ride,.,F(price))),>,0.000100),B(B(U(*,B(ride,.,F(price))),+,VA(effective_surge)),/,U(*,B(ride,.,F(price)))),1.000000));SV(round_fact_surge,B(B(VA(fact_surge),-,0.050000),round_to,0.100000));SV(round_delta,B(VA(effective_surge),round_to,B(fix,.,F(rounding_factor))));IF(B(B(B(B(FC(getMainStringFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"setcar_show_surge_or_surcharge")),R(str=std::string)),.,TF(str)),==,"show_surge"),&&,B(VA(round_fact_surge),>,1.000100)),&&,U(!,VA(is_cargo_category))),E("setcar.show_surge",VA(round_fact_surge)),IF(B(B(VA(is_cargo_category),||,B(B(FC(getMainStringFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"setcar_show_surge_or_surcharge")),R(str=std::string)),.,TF(str)),==,"show_surcharge")),&&,B(VA(effective_surge),>,0.000100)),E("setcar.show_surcharge",VA(round_delta)))));SV(surge_delta_raw,B(B(B(B(B(B(B(B(B(B(ride,.,F(price)),.,F(boarding)),+,VA(effective_surge)),+,B(B(ride,.,F(price)),.,F(distance))),+,B(B(ride,.,F(price)),.,F(time))),+,B(B(ride,.,F(price)),.,F(requirements))),+,VA(waiting)),+,VA(transit_waiting)),+,VA(destination_waiting)),-,U(*,B(ride,.,F(price)))));E("surge_delta_raw",VA(surge_delta_raw));E("surge_delta",B(VA(surge_delta_raw),round_to,B(fix,.,F(rounding_factor))));CR(boarding=B(B(B(ride,.,F(price)),.,F(boarding)),+,VA(effective_surge)),destination_waiting=VA(destination_waiting),transit_waiting=VA(transit_waiting),waiting=VA(waiting)));IF(B("setcar_show_surge_or_surcharge",in,B(fix,.,F(exps))),SV(fact_surge,T(B(U(*,B(ride,.,F(price))),>,0.000100),B(VA(price_after_surge),/,U(*,B(ride,.,F(price)))),1.000000));SV(round_fact_surge,B(B(VA(fact_surge),-,0.050000),round_to,0.100000));SV(round_delta,B(VA(delta),round_to,B(fix,.,F(rounding_factor))));IF(B(B(B(B(FC(getMainStringFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"setcar_show_surge_or_surcharge")),R(str=std::string)),.,TF(str)),==,"show_surge"),&&,B(VA(round_fact_surge),>,1.000100)),&&,U(!,VA(is_cargo_category))),E("setcar.show_surge",VA(round_fact_surge)),IF(B(B(VA(is_cargo_category),||,B(B(FC(getMainStringFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"setcar_show_surge_or_surcharge")),R(str=std::string)),.,TF(str)),==,"show_surcharge")),&&,B(VA(round_delta),>,0.000100)),E("setcar.show_surcharge",VA(round_delta)))));SV(surge_delta_raw,B(B(B(B(B(B(B(VA(boarding),+,VA(distance)),+,VA(time)),+,VA(requirements)),+,VA(waiting)),+,VA(transit_waiting)),+,VA(destination_waiting)),-,U(*,B(ride,.,F(price)))));E("surge_delta_raw",VA(surge_delta_raw));E("surge_delta",B(VA(surge_delta_raw),round_to,B(fix,.,F(rounding_factor))));CR(boarding=VA(boarding),destination_waiting=VA(destination_waiting),distance=VA(distance),requirements=VA(requirements),time=VA(time),transit_waiting=VA(transit_waiting),waiting=VA(waiting))', '2021-05-26 14:57:09.073726+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1886, 'prod_reset_big_distance', NULL, '// EFFICIENCYDEV-12845
let meters_in_5000km = 1000 * 5000;
let meters_in_500km = 1000 * 500;
let mps_to_kph_coeff = 3.6; // meters per second to kilometers to hour
let max_speed_limit_kph = 200;

let total_distance = trip.distance;
if (total_distance > meters_in_5000km) {
  return {
    distance = 0
  };
}
if (total_distance > meters_in_500km) {
  let total_time = trip.time;
  if (total_time > 0.0001) {
    let avg_speed_kph = total_distance / total_time * mps_to_kph_coeff;
    if (avg_speed_kph > max_speed_limit_kph) {
      return {
        distance = 0
      };
    }
  }
  else { // infinity speed
    return {
      distance = 0
    };
  }
}
return ride.price;', 'taximeter_only', 'ivan-popovich', 176399, 'SV(meters_in_5000km,B(1000.000000,*,5000.000000));SV(meters_in_500km,B(1000.000000,*,500.000000));SV(mps_to_kph_coeff,3.600000);SV(max_speed_limit_kph,200.000000);SV(total_distance,B(trip,.,F(distance)));IF(B(VA(total_distance),>,VA(meters_in_5000km)),CR(distance=0.000000));IF(B(VA(total_distance),>,VA(meters_in_500km)),SV(total_time,B(trip,.,F(time)));IF(B(VA(total_time),>,0.000100),SV(avg_speed_kph,B(B(VA(total_distance),/,VA(total_time)),*,VA(mps_to_kph_coeff)));IF(B(VA(avg_speed_kph),>,VA(max_speed_limit_kph)),CR(distance=0.000000)),CR(distance=0.000000)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-06-01 15:28:15.057791+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1877, 'marketing_cashback_business', NULL, '
function getMainValueFromExperiment(exp: std::unordered_map<std::string, lang::variables::ExperimentSubValue>) {
  return {val = ("main" in exp) ? (exp["main"].val as val) ? val : 0 : 0};
}

function calcCashbackPrice(cashback_rate: double) {
  let cashback_price = *ride.price * cashback_rate;
  let round_cashback_price = round_to(cashback_price, fix.rounding_factor);
  return {res = round_cashback_price};
}

function getPersonalGoalsCashbackRate() {
  let prefix = "cashback_boost_for_" + fix.category + "_percent_";
  let user_tags = fix.user_tags;

  if ((prefix + "0") in user_tags) { return {enabled=true, rate=0.00}; }
  if ((prefix + "1") in user_tags) { return {enabled=true, rate=0.01}; }
  if ((prefix + "2") in user_tags) { return {enabled=true, rate=0.02}; }
  if ((prefix + "3") in user_tags) { return {enabled=true, rate=0.03}; }
  if ((prefix + "4") in user_tags) { return {enabled=true, rate=0.04}; }
  if ((prefix + "5") in user_tags) { return {enabled=true, rate=0.05}; }
  if ((prefix + "6") in user_tags) { return {enabled=true, rate=0.06}; }
  if ((prefix + "7") in user_tags) { return {enabled=true, rate=0.07}; }
  if ((prefix + "8") in user_tags) { return {enabled=true, rate=0.08}; }
  if ((prefix + "9") in user_tags) { return {enabled=true, rate=0.09}; }
  if ((prefix + "10") in user_tags) { return {enabled=true, rate=0.1}; }
  if ((prefix + "15") in user_tags) { return {enabled=true, rate=0.15}; }
  if ((prefix + "20") in user_tags) { return {enabled=true, rate=0.2}; }
  if ((prefix + "25") in user_tags) { return {enabled=true, rate=0.25}; }
  if ((prefix + "30") in user_tags) { return {enabled=true, rate=0.3}; }
  if ((prefix + "40") in user_tags) { return {enabled=true, rate=0.4}; }
  if ((prefix + "50") in user_tags) { return {enabled=true, rate=0.5}; }
  return {enabled=false, rate=0.0};
}

function getMarketingCashbackRate() {
  // эксперимент, он и рубильник и значение
  let marketing_cashback_business = "marketing_cashback_business" in fix.exps;
  if (!marketing_cashback_business) {
    return {rate=0.0};
  }

  // кэшбек только на комфорт и комфорт+
  if (fix.category != "business" && fix.category != "comfortplus") {
    return {rate=0.0};
  }

  // только НЕплюсовикам
  if (fix.user_data.has_yaplus) {
    return {rate=0.0};
  }

  let rate = getMainValueFromExperiment(exp=fix.exps["marketing_cashback_business"]).val;
  return {rate=rate};
}

// только в России
if (fix.country_code2 != "RU") {
  return ride.price;
}

// если при этом не тратить ранее накопленный кешбек
if (fix.complements as complements) {
  return ride.price;
}

// проверка на отсутствие типа оплаты
if(fix.payment_type as payment_type) {

  // на безналичную и наличную оплату
  if (payment_type != "card" &&
    payment_type != "applepay" &&
    payment_type != "googlepay") {
      return ride.price;
  }
}


let personalGoalsCashback = getPersonalGoalsCashbackRate();
let marketingCashback = getMarketingCashbackRate();
let rate = marketingCashback.rate + personalGoalsCashback.rate;
let price = calcCashbackPrice(cashback_rate=rate).res;
if (rate > 0.000001 && price > 0.000001) {  // эпсилон-окрестность
    let meta = [
      "cashback_rate": rate,
      "cashback_discount_fixed_value": price
    ];
    let meta2 = (personalGoalsCashback.rate > 0.000001) ?
      ["-debug--personal-goals-rate": personalGoalsCashback.rate] : [];
    let meta3 = (marketingCashback.rate > 0.000001) ?
      ["marketing_cashback_business_rate": marketingCashback.rate] : [];

    return { metadata=meta + meta2 + meta3 };
}

return ride.price;
', 'both_side', 'aliev-r', 173609, 'FUNC(calcCashbackPrice,ARGS((cashback_rate,double)),B(SV(cashback_price,B(U(*,B(ride,.,F(price))),*,FA(cashback_rate,double)));SV(round_cashback_price,B(VA(cashback_price),round_to,B(fix,.,F(rounding_factor))));CR(res=VA(round_cashback_price))));FUNC(getMainValueFromExperiment,ARGS((exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),B(CR(val=T(B("main",in,FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),T(U(?,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(val))),U(*,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(val))),0.000000),0.000000))));SV(marketing_cashback_business,B("marketing_cashback_business",in,B(fix,.,F(exps))));IF(U(!,VA(marketing_cashback_business)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(B(fix,.,F(category)),!=,"business"),&&,B(B(fix,.,F(category)),!=,"comfortplus")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(fix,.,F(country_code2)),!=,"RU"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(fix,.,F(user_data)),.,F(has_yaplus)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(complements))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(payment_type))),IF(B(B(B(U(*,B(fix,.,F(payment_type))),!=,"card"),&&,B(U(*,B(fix,.,F(payment_type))),!=,"applepay")),&&,B(U(*,B(fix,.,F(payment_type))),!=,"googlepay")),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(rate,B(FC(getMainValueFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"marketing_cashback_business")),R(val=double)),.,TF(val)));SV(price,B(FC(calcCashbackPrice,NT(cashback_rate=VA(rate)),R(res=double)),.,TF(res)));IF(B(B(VA(rate),>,0.000001),&&,B(VA(price),>,0.000001)),E("marketing_cashback_business_rate",VA(rate));E("cashback_rate",VA(rate));E("cashback_discount_fixed_value",VA(price))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-27 11:14:12.539835+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1881, 'prod_yaplus_cashback', 'Кэшбэк за Яндекс.Плюс ', '
function getAvailableCashback() {
  if (fix.category_data.yaplus_coeff as yaplus_coeff) {
    return {enabled=true, rate=1-yaplus_coeff, price_decreasing_coeff=yaplus_coeff};
  }

  return {enabled=false, rate=0.0, price_decreasing_coeff=1.0};
}

// we have another rule for unite price case
let unite_total_price_enabled = "cashback_unite_total_price" in fix.exps;
if (unite_total_price_enabled) {
  return ride.price;
}

// we have another rule for using user meta
let using_user_meta_enabled = "using_user_meta_enabled" in fix.exps;
if (using_user_meta_enabled) {
  return ride.price;
}


if(fix.payment_type as payment_type) {
  let corp_type = payment_type == "corp";
  let wallet_type = payment_type == "personal_wallet";
  let corp_acc_type = payment_type == "coop_account";
  let bad_type = corp_type || wallet_type || corp_acc_type;

  if (bad_type) {
    return ride.price;
  }

  let cashback_params = getAvailableCashback();
  if (cashback_params.enabled) {
    // no cashback for cash
    if (payment_type == "cash") {
      return ride.price;
    }
    // no cashback when spending cashback
    if (fix.complements as complements) {
      return ride.price;
    }
    // too hard to calc cashback for coupon case
    if (fix.coupon as coupon) {
      if (coupon.valid) {
        return ride.price;
      }
    }
    // avoiding nan_test
    if (cashback_params.price_decreasing_coeff < 0.01) {
      return ride.price;
    }

    // это контрольная группа эксперимента Логистики
    if (cashback_params.rate < 0.01) {
      return ride.price;
    }

    let cashback_for_plus_available = "cashback_for_plus_availability" in fix.exps;
    if (!cashback_for_plus_available) {
      return ride.price;
    }

    let cashback_rate = cashback_params.rate;
    let price_decreasing_coeff = cashback_params.price_decreasing_coeff;
    let cashback_coeff = cashback_rate/price_decreasing_coeff;

    let rounded_total_price = round_to(*ride.price, fix.rounding_factor);
    let cashback_price = rounded_total_price * cashback_rate;
    let rounded_cashback_price = round_to(cashback_price, fix.rounding_factor);
    let rounded_new_ride_price = rounded_total_price - rounded_cashback_price;

    let new_price_decreasing_coeff = (*ride.price >= 1)
      ? rounded_new_ride_price/(*ride.price)
      : price_decreasing_coeff;

    if (!fix.user_data.has_yaplus) {
      return {metadata=[
        "possible_cashback_rate": cashback_rate,
        "possible_cashback_fixed_price": rounded_cashback_price
      ]};
    }

    // user hasnt accepted the new offer
    if (!fix.user_data.has_cashback_plus) {
      return ride.price;
    }

    return concat(ride.price * new_price_decreasing_coeff, {metadata=[
      "cashback_calc_coeff": cashback_coeff,
      "cashback_tariff_multiplier": price_decreasing_coeff,
      "cashback_fixed_price": rounded_cashback_price,
      "user_total_price": rounded_total_price,

      // debug
      "debug_new_price_decreasing_coeff": new_price_decreasing_coeff,
      "debug_rounded_new_ride_price": rounded_new_ride_price
    ]});
  }
  
}
return ride.price;
', 'both_side', 'aliev-r', 174610, 'FUNC(getAvailableCashback,ARGS(),B(IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),CR(enabled=true,price_decreasing_coeff=U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),rate=B(1.000000,-,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))))));CR(enabled=false,price_decreasing_coeff=1.000000,rate=0.000000)));SV(unite_total_price_enabled,B("cashback_unite_total_price",in,B(fix,.,F(exps))));IF(VA(unite_total_price_enabled),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(bad_type,B(B(VA(corp_type),||,VA(wallet_type)),||,VA(corp_acc_type)));IF(U(!,B(B(fix,.,F(user_data)),.,F(has_yaplus))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(VA(bad_type),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(enabled)),IF(U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(U(*,B(fix,.,F(payment_type))),==,"cash"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(complements))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(coupon))),IF(B(U(*,B(fix,.,F(coupon))),.,F(valid)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(price_decreasing_coeff)),<,0.010000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(rate)),<,0.010000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(cashback_for_plus_available,B("cashback_for_plus_availability",in,B(fix,.,F(exps))));IF(U(!,VA(cashback_for_plus_available)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(cashback_rate,B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(rate)));SV(price_decreasing_coeff,B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(price_decreasing_coeff)));SV(cashback_coeff,B(VA(cashback_rate),/,VA(price_decreasing_coeff)));SV(rounded_total_price,B(U(*,B(ride,.,F(price))),round_to,B(fix,.,F(rounding_factor))));SV(cashback_price,B(VA(rounded_total_price),*,VA(cashback_rate)));SV(rounded_cashback_price,B(VA(cashback_price),round_to,B(fix,.,F(rounding_factor))));SV(rounded_new_ride_price,B(VA(rounded_total_price),-,VA(rounded_cashback_price)));SV(new_price_decreasing_coeff,T(B(U(*,B(ride,.,F(price))),>=,1.000000),B(VA(rounded_new_ride_price),/,U(*,B(ride,.,F(price)))),VA(price_decreasing_coeff)));E("cashback_calc_coeff",VA(cashback_coeff));E("cashback_tariff_multiplier",VA(price_decreasing_coeff));E("cashback_fixed_price",VA(rounded_cashback_price));E("user_total_price",VA(rounded_total_price));E("debug_new_price_decreasing_coeff",VA(new_price_decreasing_coeff));E("debug_rounded_new_ride_price",VA(rounded_new_ride_price));CR(boarding=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(waiting)))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-28 15:59:33.807918+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1883, 'prod_yaplus_cashback_driver', 'Кэшбэк за Яндекс.Плюс - преобразование для водителя', '
function getAvailableCashback() {
  if (fix.category_data.yaplus_coeff as yaplus_coeff) {
    return {enabled=true, rate=1-yaplus_coeff, price_decreasing_coeff=yaplus_coeff};
  }

  return {enabled=false, rate=0.0, price_decreasing_coeff=1.0};
}

function calcCashback(base: double, rate: double) {
  let using_user_meta_enabled = "using_user_meta_enabled" in fix.exps;
  if (using_user_meta_enabled) {
    using(UserMeta) {
      if ("cashback_fixed_price" in ride.ride.user_meta) {
      	 return {
       	    value=ride.ride.user_meta["cashback_fixed_price"],
       	    metadata=[
       	      "user_meta_debug:used_meta": ride.ride.user_meta["cashback_fixed_price"]
       	    ]
	       };
      }
      return {value=base*rate, metadata=["user_meta_debug:empty_meta": 1]};
    }
    return {value=base*rate, metadata=["user_meta_debug:no_meta": 1]};
  }
  return {value=base*rate, metadata=[]};
}

// we need all this only for unite price case
let unite_total_price_enabled = "cashback_unite_total_price" in fix.exps;
if (!unite_total_price_enabled) {
  return ride.price;
}

if(fix.payment_type as payment_type) {
  let corp_type = payment_type == "corp";
  let wallet_type = payment_type == "personal_wallet";
  let corp_acc_type = payment_type == "coop_account";
  let bad_type = corp_type || wallet_type || corp_acc_type;

  if (!fix.user_data.has_yaplus) {
    return ride.price;
  }
  if (bad_type) {
    return ride.price;
  }

  let cashback_params = getAvailableCashback();
  if (cashback_params.enabled) {
    // user hasnt accepted the new offer
    if (!fix.user_data.has_cashback_plus) {
      return ride.price;
    }

    // no cashback for cash
    if (payment_type == "cash") {
      return ride.price;
    }
    // no cashback when spending cashback
    if (fix.complements as complements) {
      return ride.price;
    }

    // avoiding nan_test
    if (cashback_params.price_decreasing_coeff < 0.01) {
      return ride.price;
    }

    // если rate окажется 0
    if (cashback_params.rate < 0.01) {
      return ride.price;
    }

    let cashback_for_plus_available = "cashback_for_plus_availability" in fix.exps;
    if (!cashback_for_plus_available) {
      return ride.price;
    }

    // allow coupon only by exp
    if (fix.coupon as coupon) {
      if (coupon.valid) {
        let using_user_meta_enabled = "using_user_meta_enabled" in fix.exps;
        if (!using_user_meta_enabled) {
          return ride.price;
        }
      }
    }

    let cashback_rate = cashback_params.rate;
    let price_decreasing_coeff = cashback_params.price_decreasing_coeff;

    let rounded_total_price = round_to(*ride.price, fix.rounding_factor);
    let calc_res = calcCashback(base=rounded_total_price, rate=cashback_rate);
    let cashback_price = calc_res.value;
    let rounded_cashback_price = round_to(cashback_price, fix.rounding_factor);
    let rounded_new_ride_price = rounded_total_price - rounded_cashback_price;

    let new_price_decreasing_coeff = (*ride.price >= 1)
      ? rounded_new_ride_price/(*ride.price)
      : price_decreasing_coeff;

    let meta = calc_res.metadata;

    return concat(ride.price * new_price_decreasing_coeff, {metadata=meta});
  }

}
return ride.price;
', 'both_side', 'aliev-r', 174616, 'FUNC(getAvailableCashback,ARGS(),B(IF(U(?,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),CR(enabled=true,price_decreasing_coeff=U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))),rate=B(1.000000,-,U(*,B(B(fix,.,F(category_data)),.,F(yaplus_coeff))))));CR(enabled=false,price_decreasing_coeff=1.000000,rate=0.000000)));SV(unite_total_price_enabled,B("cashback_unite_total_price",in,B(fix,.,F(exps))));IF(U(!,VA(unite_total_price_enabled)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(payment_type))),SV(corp_type,B(U(*,B(fix,.,F(payment_type))),==,"corp"));SV(wallet_type,B(U(*,B(fix,.,F(payment_type))),==,"personal_wallet"));SV(corp_acc_type,B(U(*,B(fix,.,F(payment_type))),==,"coop_account"));SV(bad_type,B(B(VA(corp_type),||,VA(wallet_type)),||,VA(corp_acc_type)));IF(U(!,B(B(fix,.,F(user_data)),.,F(has_yaplus))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(VA(bad_type),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(enabled)),IF(U(!,B(B(fix,.,F(user_data)),.,F(has_cashback_plus))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(U(*,B(fix,.,F(payment_type))),==,"cash"),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(complements))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(fix,.,F(coupon))),IF(B(U(*,B(fix,.,F(coupon))),.,F(valid)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(price_decreasing_coeff)),<,0.010000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(B(B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(rate)),<,0.010000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(cashback_for_plus_available,B("cashback_for_plus_availability",in,B(fix,.,F(exps))));IF(U(!,VA(cashback_for_plus_available)),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(cashback_rate,B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(rate)));SV(price_decreasing_coeff,B(FC(getAvailableCashback,NT(),R(enabled=bool,price_decreasing_coeff=double,rate=double)),.,TF(price_decreasing_coeff)));SV(cashback_coeff,B(VA(cashback_rate),/,VA(price_decreasing_coeff)));SV(rounded_total_price,B(U(*,B(ride,.,F(price))),round_to,B(fix,.,F(rounding_factor))));SV(cashback_price,B(VA(rounded_total_price),*,VA(cashback_rate)));SV(rounded_cashback_price,B(VA(cashback_price),round_to,B(fix,.,F(rounding_factor))));SV(rounded_new_ride_price,B(VA(rounded_total_price),-,VA(rounded_cashback_price)));SV(new_price_decreasing_coeff,T(B(U(*,B(ride,.,F(price))),>=,1.000000),B(VA(rounded_new_ride_price),/,U(*,B(ride,.,F(price)))),VA(price_decreasing_coeff)));SV(payment_type_is_cash,T(B("payment_type_is_cash",in,B(B(ride,.,F(ride)),.,F(user_options))),B(B(B(ride,.,F(ride)),.,F(user_options)),.,"payment_type_is_cash"),0.000000));IF(B(VA(payment_type_is_cash),>,0.000000),CR(boarding=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(boarding)),destination_waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(distance)),requirements=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(requirements)),time=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(time)),transit_waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(transit_waiting)),waiting=B(B(B(ride,.,F(price)),*,VA(new_price_decreasing_coeff)),.,F(waiting))));E("unite_total_price_enabled",1.000000);E("plus_cashback_rate",VA(cashback_rate));E("cashback_calc_coeff",0.000000);E("cashback_fixed_price",VA(rounded_cashback_price));E("user_ride_price",VA(rounded_new_ride_price));E("user_total_price",VA(rounded_total_price));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-05-28 15:59:39.073357+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1885, 'prod_reset_big_time', '', '// EFFICIENCYDEV-12845
let seconds_in_week = 60 * 60 * 24 * 7;
let seconds_in_12_hours = 60 * 60 * 12;
let mps_to_kph_coeff = 3.6; // meters per second to kilometers to hour
let min_speed_limit_kph = 10;

let total_time = trip.time;
if (total_time < 0) { // EFFICIENCYDEV-12966
  return {
    time = 0
  };
}
if (total_time > seconds_in_week) {
  return {
    time = 0
  };
}
if (total_time > seconds_in_12_hours) {
  let total_distance = trip.distance;
  let avg_speed_kph = total_distance / total_time * mps_to_kph_coeff;
  if (avg_speed_kph < min_speed_limit_kph) {
     return {
        time = 0
     };
  }
}
return ride.price;', 'taximeter_only', 'ivan-popovich', 176397, 'SV(seconds_in_week,B(B(B(60.000000,*,60.000000),*,24.000000),*,7.000000));SV(seconds_in_12_hours,B(B(60.000000,*,60.000000),*,12.000000));SV(mps_to_kph_coeff,3.600000);SV(min_speed_limit_kph,10.000000);SV(total_time,B(trip,.,F(time)));IF(B(VA(total_time),<,0.000000),CR(time=0.000000));IF(B(VA(total_time),>,VA(seconds_in_week)),CR(time=0.000000));IF(B(VA(total_time),>,VA(seconds_in_12_hours)),SV(total_distance,B(trip,.,F(distance)));SV(avg_speed_kph,B(B(VA(total_distance),/,VA(total_time)),*,VA(mps_to_kph_coeff)));IF(B(VA(avg_speed_kph),<,VA(min_speed_limit_kph)),CR(time=0.000000)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-06-01 15:28:15.000068+03', NULL, false, '{}', NULL);
INSERT INTO price_modifications.rules (rule_id, name, description, source_code, policy, author, approvals_id, ast, updated, pmv_task_id, deleted, extra_return, previous_version_id) VALUES (1889, 'discount', 'Скидка (гипербола или таблица)', '
function getMainStrFromExperiment(exp: std::unordered_map<std::string, lang::variables::ExperimentSubValue>) {
  return {str = ("main" in exp) ? (exp["main"].str as str) ? str : " " : " "};
}

function abs(val : double) {
    return {res = (val < 0) ? -val : val};
}

function min(a : double, b : double) {
  return {res = (a < b) ? a : b};
}

function max(a : double, b : double) {
  return {res = (a > b) ? a : b};
}

function minBetweenOptionals(a: std::optional<double>, b_value:double, b_is_set: bool) {
  if (a as a_value) {
    if (b_is_set) {
      return {value=min(a=a_value, b=b_value).res, is_set=true};
    }
    return {value=a_value, is_set=true};
  }
  return {value=b_value, is_set=b_is_set};
}

function calculateHyperbolaDiscountPercent(hyperbolas : clients::discounts::HyperbolasData, price : double) {
    // выбираем гиперболу по порогу
    let hyperbola = (price < hyperbolas.threshold)
        ? hyperbolas.hyperbola_lower
        : hyperbolas.hyperbola_upper;

    // избегаем деления на 0
    if (abs(val=price + hyperbola.c).res < 0.0001) {
        return {res = 0};
    }

    // считаем по формуле гиперболы
    return {res = (hyperbola.p + hyperbola.a / (price + hyperbola.c))};
}

function processTableElement(elem : clients::discounts::TableDataA,
                             has_result: bool,
                             result : double,
                             price : double,
                             first_iteration : bool,
                             prev_elem_price : double,
                             prev_elem_coeff : double) {
    // если результат уже получен, то сразу отдаём его обратно
    if (has_result) {
        return {
            has_result = true,
            result = result,
            // следующие 4 строчки одинаковые во всех return
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // если цена меньше первой цены в таблице, то используем первый элемент
    if (first_iteration && price < elem.price) {
        return {
            has_result = true,
            result = elem.coeff,
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // если цена между предыдущим элементом таблицы и текущим
    if (!first_iteration && prev_elem_price <= price && price < elem.price) {
        // избегаем деления на 0
        if (abs(val=elem.price - prev_elem_price).res < 0.0001) {
            return {
                has_result = true,
                result = 0,
                price = price,
                first_iteration = false,
                prev_elem_price = elem.price,
                prev_elem_coeff = elem.coeff
            };
        }
        // делаем линейную интерполяцию
        return {
            has_result = true,
            result = prev_elem_coeff
                + (elem.coeff - prev_elem_coeff) * (price - prev_elem_price)
                    / (elem.price - prev_elem_price),
            price = price,
            first_iteration = false,
            prev_elem_price = elem.price,
            prev_elem_coeff = elem.coeff
        };
    }

    // результат ещё не получен
    return {
        has_result = false,
        result = result,
        price = price,
        first_iteration = false,
        prev_elem_price = elem.price,
        prev_elem_coeff = elem.coeff
    };
}

function calculateTableDiscountPercent(table : std::vector<clients::discounts::TableDataA>, price : double) {
    // проходим по элементам таблицы функцией processTableElement
    let process_table_result = fold(table as elem, processTableElement, {
        has_result = false,
        result = 0,
        price = price,
        first_iteration = true,
        prev_elem_price = 0,
        prev_elem_coeff = 0
    });

    // если результат получен, то отдаём его
    if (process_table_result.has_result) {
        return {res = process_table_result.result};
    }

    // если пришли сюда, то значит цена больше или равна последней цене в таблице, используем последний элемент
    return {res = process_table_result.prev_elem_coeff};
}

function normalizeToMinMax(coeff : double, restrictions : clients::discounts::DiscountRestrictions) {
    // ограничение сверху максимально допустимым значением
    let coeff_limited_to_max = min(a = coeff, b = restrictions.max_discount_coeff).res;
    // если коэффициент меньше минимально допустимого, то сбрасываем в 0 (иначе скидка слишком мелкая)
    return {
        res = (coeff_limited_to_max < restrictions.min_discount_coeff) ? 0 : coeff_limited_to_max
    };
}

function normalizeByMaxAbsoluteValue(coeff : double, price: double, 
                                     max_absolute_value : double) {
    if (price * coeff > max_absolute_value && price > 0.0001) {
        return {
            res = min(a = max(a = max_absolute_value / price, b = 0).res,
                      b = 1).res
        };
    }
    return {res = coeff};
}

function getPreviousCategory() {
  if (fix.category == "business") {
    return {res="econom"};
  } else if (fix.category == "uberselect") {
    return {res="uberx"};
  }
  return {res=" "};
}

// Получаем под экспериментом ограничение максимального значения скидки 
// из значения расчитанного для категории эконом (unberx для uberselect)
// Добавляется в рамках EFFICIENCYDEV-12250
function fetchDiscountRestrictionFromPrevCategory(discount_class: std::string) {
  if ("restrict_absolute_discount" in fix.exps && discount_class == "discounts-calculator") {
    let previous_category = getPreviousCategory().res;
    if (previous_category != " ") {
      let discount_type = getMainStrFromExperiment(exp=fix.exps["restrict_absolute_discount"]).str;
      if (discount_type == "no_discount") {
        return {value=0, is_set=true};
      }
      if (discount_type == "from_previous_category") {
        if (fix.previously_calculated_categories as previously_calculated_categories) {
          if (previous_category in previously_calculated_categories) {
            let econom_meta = previously_calculated_categories[previous_category].user.final_prices["main"].meta;
            if ("discount_delta_raw" in econom_meta) {
              let discount_delta_raw = econom_meta["discount_delta_raw"];
              return {value=-discount_delta_raw, is_set=true};
            }
          }
        }
        // Сюда попадём в том случае, когда не считали предыдущую категорию (например, пересчёт отложки).
        // При этом убираем скидку.
        return {value=0, is_set=true};
      }
    }
  }
  return {value=0, is_set=false};
}


if (fix.discount as discount) {
    // не применять эту скидку, если она не должна добавлять себя
    // в разницу между между зачёркнутой ценой и обычной
    if (discount.is_price_strikethrough as is_price_strikethrough) {
        if (!is_price_strikethrough) {
            return ride.price;
        }
    }

    let restrictions = discount.restrictions;

    let meta1 = [
      "discount_price": *ride.price  // цена ДО применения скидки, на неподходящее название уже заложился DWH :(
    ];

    // скидка действует на все компоненты цены, кроме ожиданий
    let affected_price = *ride.price - ride.price.waiting
                                     - ride.price.transit_waiting
                                     - ride.price.destination_waiting;

    let percent = (discount.calc_data_hyperbolas as hyp)                                   // если заданы гиперболы
        ? calculateHyperbolaDiscountPercent(hyperbolas = hyp, price = affected_price).res  // считаем скидку по формуле гиперболы
        : (discount.calc_data_table_data as tbl)                                           // если задана таблица
            ? calculateTableDiscountPercent(table = tbl, price = affected_price).res       // считаем скидку по таблице
            : 0;                                                                           // иначе нет скидки

    // Под экспериментом ограничиваем скидку максимальным значением как в экономе
    let discount_class = (discount.discount_class as discount_class) ? discount_class : " ";
    let econom_discount_restriction = fetchDiscountRestrictionFromPrevCategory(discount_class = discount_class);

    let max_absolute_value_opt = minBetweenOptionals(a = restrictions.max_absolute_value,
                                                     b_value = econom_discount_restriction.value,
                                                     b_is_set = econom_discount_restriction.is_set);

    let coeff1 = percent * 0.01;
    let coeff2 = normalizeToMinMax(coeff = coeff1, restrictions = restrictions).res;
    let coeff3 = (max_absolute_value_opt.is_set)
        ? normalizeByMaxAbsoluteValue(coeff = coeff2,
                                      price = affected_price,
                                      max_absolute_value = max_absolute_value_opt.value).res
        : coeff2;
    if (coeff3 <= 0) {
        return {metadata = meta1};
    }
    let coeff_final = min(a = coeff3, b = 1).res;
    let delta = -affected_price * coeff_final;

    let meta2 = [
      // если должна работать как скидка
      "discount_value": coeff_final,
      "discount_delta_raw": delta
    ];

    let mult = 1 - coeff_final;
    return {
        boarding = ride.price.boarding * mult,
        distance = ride.price.distance * mult,
        time = ride.price.time * mult,
        requirements = ride.price.requirements * mult,
        waiting = ride.price.waiting,
        transit_waiting = ride.price.transit_waiting,
        destination_waiting = ride.price.destination_waiting,
        metadata = meta1 + meta2
    };
}

return ride.price;', 'both_side', 'shchesnyak', 176502, 'FUNC(abs,ARGS((val,double)),B(CR(res=T(B(FA(val,double),<,0.000000),U(-,FA(val,double)),FA(val,double)))));FUNC(applyNewbieCoefficients,ARGS((coeff,double),(restrictions,clients::discounts::DiscountRestrictions)),B(SV(newbie_max_coeff,T(U(?,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(newbie_max_coeff))),U(*,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(newbie_max_coeff))),1.000000));SV(newbie_num_coeff,T(U(?,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(newbie_num_coeff))),U(*,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(newbie_num_coeff))),0.000000));SV(completed_count,T(U(?,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(completed_on_special_conditions_count))),U(*,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(completed_on_special_conditions_count))),0.000000));CR(res=B(FA(coeff,double),*,B(VA(newbie_max_coeff),-,B(VA(newbie_num_coeff),*,VA(completed_count)))))));FUNC(calculateHyperbolaDiscountPercent,ARGS((hyperbolas,clients::discounts::HyperbolasData),(price,double)),B(IF(B(B(FC(abs,NT(val=B(FA(price,double),+,B(T(B(FA(price,double),<,B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(threshold))),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_lower)),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_upper))),.,F(c)))),R(res=double)),.,TF(res)),<,0.000100),CR(res=0.000000));CR(res=B(B(T(B(FA(price,double),<,B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(threshold))),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_lower)),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_upper))),.,F(p)),+,B(B(T(B(FA(price,double),<,B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(threshold))),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_lower)),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_upper))),.,F(a)),/,B(FA(price,double),+,B(T(B(FA(price,double),<,B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(threshold))),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_lower)),B(FA(hyperbolas,clients::discounts::HyperbolasData),.,F(hyperbola_upper))),.,F(c))))))));FUNC(calculateTableDiscountPercent,ARGS((price,double),(table,std::vector<clients::discounts::TableDataA>)),B(IF(B(FL(FA(table,std::vector<clients::discounts::TableDataA>),elem,NT(first_iteration=true,has_result=false,prev_elem_coeff=0.000000,prev_elem_price=0.000000,price=FA(price,double),result=0.000000),NT(first_iteration=T(FA(has_result,bool),false,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),false,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),false,false),false))),has_result=T(FA(has_result,bool),true,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),true,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),true,true),false))),prev_elem_coeff=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))))),prev_elem_price=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(price)),B(FA(elem,clients::discounts::TableDataA),.,F(price))),B(FA(elem,clients::discounts::TableDataA),.,F(price))))),price=T(FA(has_result,bool),FA(price,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),FA(price,double),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),FA(price,double),FA(price,double)),FA(price,double)))),result=T(FA(has_result,bool),FA(result,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),0.000000,B(FA(prev_elem_coeff,double),+,B(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),-,FA(prev_elem_coeff,double)),*,B(FA(price,double),-,FA(prev_elem_price,double))),/,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))))),FA(result,double)))))),.,TF(has_result)),CR(res=B(FL(FA(table,std::vector<clients::discounts::TableDataA>),elem,NT(first_iteration=true,has_result=false,prev_elem_coeff=0.000000,prev_elem_price=0.000000,price=FA(price,double),result=0.000000),NT(first_iteration=T(FA(has_result,bool),false,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),false,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),false,false),false))),has_result=T(FA(has_result,bool),true,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),true,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),true,true),false))),prev_elem_coeff=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))))),prev_elem_price=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(price)),B(FA(elem,clients::discounts::TableDataA),.,F(price))),B(FA(elem,clients::discounts::TableDataA),.,F(price))))),price=T(FA(has_result,bool),FA(price,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),FA(price,double),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),FA(price,double),FA(price,double)),FA(price,double)))),result=T(FA(has_result,bool),FA(result,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),0.000000,B(FA(prev_elem_coeff,double),+,B(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),-,FA(prev_elem_coeff,double)),*,B(FA(price,double),-,FA(prev_elem_price,double))),/,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))))),FA(result,double)))))),.,TF(result))));CR(res=B(FL(FA(table,std::vector<clients::discounts::TableDataA>),elem,NT(first_iteration=true,has_result=false,prev_elem_coeff=0.000000,prev_elem_price=0.000000,price=FA(price,double),result=0.000000),NT(first_iteration=T(FA(has_result,bool),false,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),false,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),false,false),false))),has_result=T(FA(has_result,bool),true,T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),true,T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),true,true),false))),prev_elem_coeff=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff))))),prev_elem_price=T(FA(has_result,bool),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(price)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),B(FA(elem,clients::discounts::TableDataA),.,F(price)),B(FA(elem,clients::discounts::TableDataA),.,F(price))),B(FA(elem,clients::discounts::TableDataA),.,F(price))))),price=T(FA(has_result,bool),FA(price,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),FA(price,double),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),FA(price,double),FA(price,double)),FA(price,double)))),result=T(FA(has_result,bool),FA(result,double),T(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),T(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),T(B(T(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double)),<,0.000000),U(-,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),<,0.000100),0.000000,B(FA(prev_elem_coeff,double),+,B(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),-,FA(prev_elem_coeff,double)),*,B(FA(price,double),-,FA(prev_elem_price,double))),/,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))))),FA(result,double)))))),.,TF(prev_elem_coeff)))));FUNC(fetchDiscountRestrictionFromPrevCategory,ARGS((discount_class,std::string)),B(IF(B(B("restrict_absolute_discount",in,B(fix,.,F(exps))),&&,B(FA(discount_class,std::string),==,"discounts-calculator")),IF(B(B(FC(getPreviousCategory,NT(),R(res=std::string)),.,TF(res)),!=," "),IF(B(B(FC(getMainStrFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"restrict_absolute_discount")),R(str=std::string)),.,TF(str)),==,"no_discount"),CR(is_set=true,value=0.000000));IF(B(B(FC(getMainStrFromExperiment,NT(exp=B(B(fix,.,F(exps)),.,"restrict_absolute_discount")),R(str=std::string)),.,TF(str)),==,"from_previous_category"),IF(U(?,B(fix,.,F(previously_calculated_categories))),IF(B(B(FC(getPreviousCategory,NT(),R(res=std::string)),.,TF(res)),in,U(*,B(fix,.,F(previously_calculated_categories)))),IF(B("discount_delta_raw",in,B(B(B(B(B(U(*,B(fix,.,F(previously_calculated_categories))),.,B(FC(getPreviousCategory,NT(),R(res=std::string)),.,TF(res))),.,F(user)),.,F(final_prices)),.,"main"),.,F(meta))),SV(discount_delta_raw,B(B(B(B(B(B(U(*,B(fix,.,F(previously_calculated_categories))),.,B(FC(getPreviousCategory,NT(),R(res=std::string)),.,TF(res))),.,F(user)),.,F(final_prices)),.,"main"),.,F(meta)),.,"discount_delta_raw"));CR(is_set=true,value=U(-,VA(discount_delta_raw))))));CR(is_set=true,value=0.000000))));CR(is_set=false,value=0.000000)));FUNC(getMainStrFromExperiment,ARGS((exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),B(CR(str=T(B("main",in,FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>)),T(U(?,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(str))),U(*,B(B(FA(exp,std::unordered_map<std::string,lang::variables::ExperimentSubValue>),.,"main"),.,F(str)))," ")," "))));FUNC(getPreviousCategory,ARGS(),B(IF(B(B(fix,.,F(category)),==,"business"),CR(res="econom"),IF(B(B(fix,.,F(category)),==,"uberselect"),CR(res="uberx")));CR(res=" ")));FUNC(max,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),>,FA(b,double)),FA(a,double),FA(b,double)))));FUNC(min,ARGS((a,double),(b,double)),B(CR(res=T(B(FA(a,double),<,FA(b,double)),FA(a,double),FA(b,double)))));FUNC(minBetweenOptionals,ARGS((a,std::optional<double>),(b_is_set,bool),(b_value,double)),B(IF(U(?,FA(a,std::optional<double>)),IF(FA(b_is_set,bool),CR(is_set=true,value=B(FC(min,NT(a=U(*,FA(a,std::optional<double>)),b=FA(b_value,double)),R(res=double)),.,TF(res))));CR(is_set=true,value=U(*,FA(a,std::optional<double>))));CR(is_set=FA(b_is_set,bool),value=FA(b_value,double))));FUNC(normalizeByMaxAbsoluteValue,ARGS((coeff,double),(max_absolute_value,double),(price,double)),B(IF(B(B(B(FA(price,double),*,FA(coeff,double)),>,FA(max_absolute_value,double)),&&,B(FA(price,double),>,0.000100)),CR(res=B(FC(min,NT(a=B(FC(max,NT(a=B(FA(max_absolute_value,double),/,FA(price,double)),b=0.000000),R(res=double)),.,TF(res)),b=1.000000),R(res=double)),.,TF(res))));CR(res=FA(coeff,double))));FUNC(normalizeToMinMax,ARGS((coeff,double),(restrictions,clients::discounts::DiscountRestrictions)),B(SV(coeff_limited_to_max,B(FC(min,NT(a=FA(coeff,double),b=B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(max_discount_coeff))),R(res=double)),.,TF(res)));CR(res=T(B(VA(coeff_limited_to_max),<,B(FA(restrictions,clients::discounts::DiscountRestrictions),.,F(min_discount_coeff))),0.000000,VA(coeff_limited_to_max)))));FUNC(processTableElement,ARGS((elem,clients::discounts::TableDataA),(first_iteration,bool),(has_result,bool),(prev_elem_coeff,double),(prev_elem_price,double),(price,double),(result,double)),B(IF(FA(has_result,bool),CR(first_iteration=false,has_result=true,prev_elem_coeff=B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),prev_elem_price=B(FA(elem,clients::discounts::TableDataA),.,F(price)),price=FA(price,double),result=FA(result,double)));IF(B(FA(first_iteration,bool),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),CR(first_iteration=false,has_result=true,prev_elem_coeff=B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),prev_elem_price=B(FA(elem,clients::discounts::TableDataA),.,F(price)),price=FA(price,double),result=B(FA(elem,clients::discounts::TableDataA),.,F(coeff))));IF(B(B(U(!,FA(first_iteration,bool)),&&,B(FA(prev_elem_price,double),<=,FA(price,double))),&&,B(FA(price,double),<,B(FA(elem,clients::discounts::TableDataA),.,F(price)))),IF(B(B(FC(abs,NT(val=B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))),R(res=double)),.,TF(res)),<,0.000100),CR(first_iteration=false,has_result=true,prev_elem_coeff=B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),prev_elem_price=B(FA(elem,clients::discounts::TableDataA),.,F(price)),price=FA(price,double),result=0.000000));CR(first_iteration=false,has_result=true,prev_elem_coeff=B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),prev_elem_price=B(FA(elem,clients::discounts::TableDataA),.,F(price)),price=FA(price,double),result=B(FA(prev_elem_coeff,double),+,B(B(B(B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),-,FA(prev_elem_coeff,double)),*,B(FA(price,double),-,FA(prev_elem_price,double))),/,B(B(FA(elem,clients::discounts::TableDataA),.,F(price)),-,FA(prev_elem_price,double))))));CR(first_iteration=false,has_result=false,prev_elem_coeff=B(FA(elem,clients::discounts::TableDataA),.,F(coeff)),prev_elem_price=B(FA(elem,clients::discounts::TableDataA),.,F(price)),price=FA(price,double),result=FA(result,double))));IF(U(?,B(fix,.,F(discount))),IF(U(?,B(U(*,B(fix,.,F(discount))),.,F(is_price_strikethrough))),IF(U(!,U(*,B(U(*,B(fix,.,F(discount))),.,F(is_price_strikethrough)))),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))));IF(B(B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(recalc_type)),==,clients::discounts::RecalcType::kSurgePrice),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));E("discount_price",U(*,B(ride,.,F(price))));SV(affected_price,B(B(B(U(*,B(ride,.,F(price))),-,B(B(ride,.,F(price)),.,F(waiting))),-,B(B(ride,.,F(price)),.,F(transit_waiting))),-,B(B(ride,.,F(price)),.,F(destination_waiting))));SV(percent,T(U(?,B(U(*,B(fix,.,F(discount))),.,F(calc_data_hyperbolas))),B(FC(calculateHyperbolaDiscountPercent,NT(hyperbolas=U(*,B(U(*,B(fix,.,F(discount))),.,F(calc_data_hyperbolas))),price=VA(affected_price)),R(res=double)),.,TF(res)),T(U(?,B(U(*,B(fix,.,F(discount))),.,F(calc_data_table_data))),B(FC(calculateTableDiscountPercent,NT(price=VA(affected_price),table=U(*,B(U(*,B(fix,.,F(discount))),.,F(calc_data_table_data)))),R(res=double)),.,TF(res)),0.000000)));SV(coeff_initial,B(VA(percent),*,0.010000));SV(coeff1,B(FC(applyNewbieCoefficients,NT(coeff=VA(coeff_initial),restrictions=B(U(*,B(fix,.,F(discount))),.,F(restrictions))),R(res=double)),.,TF(res)));SV(coeff2,B(FC(normalizeToMinMax,NT(coeff=VA(coeff1),restrictions=B(U(*,B(fix,.,F(discount))),.,F(restrictions))),R(res=double)),.,TF(res)));SV(coeff3,T(B(FC(minBetweenOptionals,NT(a=B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(max_absolute_value)),b_is_set=B(FC(fetchDiscountRestrictionFromPrevCategory,NT(discount_class=T(U(?,B(U(*,B(fix,.,F(discount))),.,F(discount_class))),U(*,B(U(*,B(fix,.,F(discount))),.,F(discount_class)))," ")),R(is_set=bool,value=double)),.,TF(is_set)),b_value=B(FC(fetchDiscountRestrictionFromPrevCategory,NT(discount_class=T(U(?,B(U(*,B(fix,.,F(discount))),.,F(discount_class))),U(*,B(U(*,B(fix,.,F(discount))),.,F(discount_class)))," ")),R(is_set=bool,value=double)),.,TF(value))),R(is_set=bool,value=double)),.,TF(is_set)),B(FC(normalizeByMaxAbsoluteValue,NT(coeff=VA(coeff2),max_absolute_value=B(FC(minBetweenOptionals,NT(a=B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(max_absolute_value)),b_is_set=B(FC(fetchDiscountRestrictionFromPrevCategory,NT(discount_class=T(U(?,B(U(*,B(fix,.,F(discount))),.,F(discount_class))),U(*,B(U(*,B(fix,.,F(discount))),.,F(discount_class)))," ")),R(is_set=bool,value=double)),.,TF(is_set)),b_value=B(FC(fetchDiscountRestrictionFromPrevCategory,NT(discount_class=T(U(?,B(U(*,B(fix,.,F(discount))),.,F(discount_class))),U(*,B(U(*,B(fix,.,F(discount))),.,F(discount_class)))," ")),R(is_set=bool,value=double)),.,TF(value))),R(is_set=bool,value=double)),.,TF(value)),price=VA(affected_price)),R(res=double)),.,TF(res)),VA(coeff2)));IF(B(VA(coeff3),<=,0.000000),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));SV(coeff_final,B(FC(min,NT(a=VA(coeff3),b=1.000000),R(res=double)),.,TF(res)));IF(B(U(*,B(fix,.,F(discount))),.,F(is_cashback)),IF(T(U(?,B(fix,.,F(complements))),U(?,B(B(fix,.,F(complements)),.,F(personal_wallet))),false),CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));IF(U(?,B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(max_absolute_value))),E("cashback_max_value",U(*,B(B(U(*,B(fix,.,F(discount))),.,F(restrictions)),.,F(max_absolute_value)))));E("cashback_rate",VA(coeff_final));IF(U(?,B(U(*,B(fix,.,F(discount))),.,F(description))),IF(B(B(U(*,B(U(*,B(fix,.,F(discount))),.,F(description))),==,"mc_cashback_ultima_plus"),||,B(U(*,B(U(*,B(fix,.,F(discount))),.,F(description))),==,"mastercard_comforts_cashback_summer")),E("cashback_sponsor:mastercard",1.000000));IF(B(U(*,B(U(*,B(fix,.,F(discount))),.,F(description))),==,"mastercard_otkrytie_ultima_cashback_2021"),E("cashback_sponsor:otkrytie_mastercard",1.000000)));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));E("discount_value",VA(coeff_final));SV(delta,B(U(-,VA(affected_price)),*,VA(coeff_final)));E("discount_delta_raw",VA(delta));SV(mult,B(1.000000,-,VA(coeff_final)));CR(boarding=B(B(B(ride,.,F(price)),.,F(boarding)),*,VA(mult)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(B(ride,.,F(price)),.,F(distance)),*,VA(mult)),requirements=B(B(B(ride,.,F(price)),.,F(requirements)),*,VA(mult)),time=B(B(B(ride,.,F(price)),.,F(time)),*,VA(mult)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting))));CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)),distance=B(B(ride,.,F(price)),.,F(distance)),requirements=B(B(ride,.,F(price)),.,F(requirements)),time=B(B(ride,.,F(price)),.,F(time)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),waiting=B(B(ride,.,F(price)),.,F(waiting)))', '2021-06-01 15:48:13.185164+03', NULL, false, '{}', NULL);


--
-- PostgreSQL database dump complete
--

