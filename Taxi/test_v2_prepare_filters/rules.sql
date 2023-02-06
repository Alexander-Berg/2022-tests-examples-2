INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'coupon', '', 'both_side', '200ok', 1, ''),
  (2, 'yaplus', '', 'both_side', '200ok', 2, ''),
  (3, 'paid_supply', '', 'both_side', '200ok', 3, ''),
  (4, 'requirements', '', 'both_side', '200ok', 4, ''),
  (5, 'surge', '', 'both_side', '200ok', 5, ''),
  (6, 'user_discount', '', 'both_side', '200ok', 6, ''),
  (7, 'waiting_in_A', '', 'both_side', '200ok', 7, ''),
  (8, 'waiting_in_transit', '', 'both_side', '200ok', 8, ''),

  (9, 'test_rule_1', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 1)/ *ride.price) * ride.price;', 'both_side', '200ok', 9, ''),
  (10, 'test_rule_2_for_taximeter', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 2)/ *ride.price) * ride.price;', 'taximeter_only', '200ok', 10, ''),
  (11, 'test_rule_3_for_backend', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 4)/ *ride.price) * ride.price;', 'backend_only', '200ok', 11, ''),
  (12, 'test_rule_4_for_driver', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 8)/ *ride.price) * ride.price;', 'both_side', '200ok', 12, ''),
  (13, 'test_rule_5_for_user', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 16)/ *ride.price) * ride.price;', 'both_side', '200ok', 13, ''),
  (14, 'test_rule_6_for_antisurge', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 32)/ *ride.price) * ride.price;', 'both_side', '200ok', 14, ''),
  (15, 'test_rule_7_for_total', 'if (fix.category != "vip") { return ride.price; } return ((*ride.price + 64)/ *ride.price) * ride.price;', 'both_side', '200ok', 15, ''),

  (16, 'return_time', 'if (fix.category != "ubernight") { return ride.price; } return (trip.time/ *ride.price) * ride.price;', 'both_side', '200ok', 16, ''),

  (17, 'combo_order_modification', 'if (fix.category == "vip") { return ride.price; } return ((*ride.price + 1)/ *ride.price) * ride.price;', 'both_side', '200ok', 17, ''),
  (18, 'combo_inner_modification', 'if (fix.category == "vip") { return ride.price; } return ((*ride.price + 10)/ *ride.price) * ride.price;', 'both_side', '200ok', 18, ''),
  (19, 'combo_outer_modification', 'if (fix.category == "vip") { return ride.price; } return ((*ride.price - 10)/ *ride.price) * ride.price;', 'both_side', '200ok', 19, ''),
  (20, 'combo_modification', 'if (fix.category != "ubernight") { return ride.price; } return ((*ride.price - 5)/ *ride.price) * ride.price;', 'both_side', '200ok', 20, ''),
  (21, 'kekw_modification', 'if (fix.alt_offer_discount as alt_offer_discount) { if ("kekw" in alt_offer_discount.params) { return alt_offer_discount.params["kekw"] * ride.price; } } return ride.price;', 'both_side', '200ok', 21, '')


;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category != "maybach" && fix.category != "business") {
  return ride.price;
}
let price = *ride.price;
if (fix.coupon as coupon) {
  if (coupon.percent as percent) {
    let percent_value = price * percent / 100;
    if (coupon.limit as limit) {
      return ((price - ((limit < percent_value) ? limit : percent_value)) / *ride.price) * ride.price;
    }
    return ((price - percent_value) / *ride.price) * ride.price;
  }
  return ((price - coupon.value) / *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 1;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category == "comfortplus" || fix.category == "maybach") {
  if (fix.user_data.has_yaplus) {
    if (fix.category_data.yaplus_coeff as yaplus_coeff) {
      return ride.price * yaplus_coeff;
    }
  }
}
return ride.price;'
WHERE rule_id = 2;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category == "minivan" || fix.category == "demostand") {
  if (fix.paid_supply_price as paid_supply_price) {
    return ((*ride.price + paid_supply_price)/ *ride.price) * ride.price;
  }
}
return ride.price;'
WHERE rule_id = 3;


UPDATE price_modifications.rules
    SET source_code = 'with (simple_cost = 0) generate(req : fix.requirements.simple)
    let rprice = (req in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[req] : 0;
endgenerate(simple_cost = simple_cost + rprice)
with (select_cost = 0) generate(req : fix.requirements.select)
    let rname = req.first;
    with (options_cost=0) generate(opt: req.second)
        let oname = (opt.independent) ? rname + "." + opt.name : rname;
        let ocost = (oname in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[oname] : 0;
    endgenerate(options_cost=options_cost + ocost)
endgenerate(select_cost = select_cost + options_cost)
return {
    requirements = simple_cost + select_cost
};'
WHERE rule_id = 4;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category == "econom" || fix.category == "comfortplus") {
    let alpha = (fix.surge_params.surcharge_alpha as surge_alpha) ? surge_alpha : 1;
    let beta = (fix.surge_params.surcharge_beta as surge_beta) ? surge_beta : 0;
    let surcharge = (fix.surge_params.surcharge as surge_surcharge) ? surge_surcharge : 0;

    return ((*ride.price * (alpha * fix.surge_params.value + beta) + beta * surcharge)/ *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 5;


UPDATE price_modifications.rules
    SET source_code = 'return ride.price;'
WHERE rule_id = 6;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category == "business" || fix.category == "minivan") {
  let waiting_price = (fix.tariff.transfer_prices as transfer_prices) ? transfer_prices.waiting_price : fix.tariff.waiting_price;
  let free_waiting_time = waiting_price.free_waiting_time;
  let paid_waiting_time = ride.ride.waiting_time - free_waiting_time;
  if (paid_waiting_time > 0) {
    let price_per_minute = waiting_price.price_per_minute;
    return {waiting = paid_waiting_time * price_per_minute / 60};
  }
}
return ride.price;'
WHERE rule_id = 7;


UPDATE price_modifications.rules
    SET source_code = '
if (fix.category == "cargo" || fix.category == "demostand") {
  let name = "waiting_in_transit";
  let costper = (name in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[name] : 0;

  let time = ride.ride.waiting_in_transit_time;

  if(time > 0) {
    let cost = ride.price.transit_waiting + time*costper;
    return { transit_waiting = cost };
  }
}
return ride.price;'
WHERE rule_id = 8;
