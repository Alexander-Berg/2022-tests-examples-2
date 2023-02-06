function get_free(supply) {
  for (let i = 0; i < supply.length; i++) {
    let time_quant = supply[i];
    if (time_quant.to == 0) {
      let res = 0;
      for (let j = 0; j < time_quant.values.length; j++) {
        res += time_quant.values[j].value.total;
      }
      return res;
    }
  }
  return 0;
}

function get_conditionally_free(supply, cond_free_threshold) {
  let res = 0;
  for (let i = 0; i < supply.length; i++) {
    let time_quant = supply[i];
    if (time_quant.to == 0) continue;

    let avg_time = (time_quant.to + time_quant.from) / 2;
    if (avg_time > cond_free_threshold) continue;

    let weight = (cond_free_threshold - avg_time) / cond_free_threshold;
    for (let j = 0; j < time_quant.values.length; j++) {
      res += time_quant.values[j].value.total * weight;
    }
  }
  return res;
}

function get_busy(demand) {
  for (let i = 0; i < demand.length; i++) {
    let time_quant = demand[i];
    if (time_quant.to == 0) {
      let res = 0;
      for (let j = 0; j < time_quant.values.length; j++) {
        res += time_quant.values[j].value.total;
      }
      return res;
    }
  }
  return 0;
}

function get_conditionally_busy(demand, cond_busy_threshold) {
  let res = 0;
  for (let i = 0; i < demand.length; i++) {
    let time_quant = demand[i];
    if (time_quant.to == 0) continue;

    let avg_time = (time_quant.to + time_quant.from) / 2;
    if (avg_time > cond_busy_threshold) continue;

    let weight = (cond_busy_threshold - avg_time) / cond_busy_threshold;
    for (let j = 0; j < time_quant.values.length; j++) {
      res += time_quant.values[j].value.total * weight;
    }
  }
  return res;
}

let damper_x = place_settings.damper_x;
let damper_y = place_settings.damper_y;
let cond_free_threshold = place_settings.cond_free_threshold;
let cond_busy_threshold = place_settings.cond_busy_threshold;

let supply_quantums = place_supply.supply;
let free = get_free(supply_quantums);
let conditionally_free =
    get_conditionally_free(supply_quantums, cond_free_threshold);

let demand_quantums = place_supply.demand;
let busy = get_busy(demand_quantums);
let conditionally_busy =
    get_conditionally_busy(demand_quantums, cond_busy_threshold);

let load_level = (busy + conditionally_busy + damper_x) /
    (busy + conditionally_busy + free + conditionally_free + damper_y) * 100;

log.info('damper_x: ' + damper_x);
log.info('damper_y: ' + damper_y);
log.info('cond_free_threshold: ' + cond_free_threshold);
log.info('cond_busy_threshold: ' + cond_busy_threshold);
log.info('free: ' + free);
log.info('conditionally_free: ' + conditionally_free);
log.info('busy: ' + busy);
log.info('conditionally_busy: ' + conditionally_busy);
log.info('load_level: ' + load_level);

return {load_level: load_level, free: free, busy: busy};
