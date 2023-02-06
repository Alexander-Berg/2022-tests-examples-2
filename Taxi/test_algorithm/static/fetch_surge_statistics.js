function stage(point_a, user_id, phone_id, distance, payment_type,
               orders_complete, point_b, tariff_zone, radius, client,
               drivers_by_category, reposition_by_category, pins, pins_b,
               pins_order, pins_driver, prev_pins, pins_meta_by_category,
               categories) {
  let req = {
    point_a: point_a,
    user_id: user_id,
    phone_id: phone_id,
    distance: distance,
    payment_type: payment_type,
    orders_complete: orders_complete,
    point_b: point_b,
    tariff_zone: tariff_zone,
    radius: radius,
    client: client,
  }

  Object.keys(req).forEach(key => {
    if (req[key] === undefined) {
      delete req[key];
    }
  })

  if (req.user_id === undefined) {
    req.user_id = "";
  }

  let by_category = {}
  for (let category of categories) {
    let drivers = drivers_by_category[category];
    let cat_req = {
      pins: pins,
      pins_b: pins_b,
      pins_order: pins_order,
      prev_pins: prev_pins,
      free: drivers.free,
      free_chain: drivers.free_chain,
      total: drivers.total
    }
    if (!Object.values(cat_req).every(is_present)) {
      // Missing required field
      continue;
    }

    if (reposition_by_category && reposition_by_category[category]) {
      let reposition = reposition_by_category[category];
      cat_req.reposition = {
        free: reposition.free,
        free_chain: reposition.free_chain,
        total: reposition.total
      }
    }

    if (pins_meta_by_category && pins_meta_by_category[category]) {
      let meta = pins_meta_by_category[category];
      cat_req.prev_eta = meta.estimated_waiting;
      cat_req.prev_surge = meta.surge;
      // These values not used by ML
      cat_req.prev_free = 0;
      cat_req.prev_chain = 0;
      cat_req.prev_total = 0;
    }

    by_category[category] = cat_req;
  }
  req.by_category = by_category;
  return {surge_statistics_info: req};
}
