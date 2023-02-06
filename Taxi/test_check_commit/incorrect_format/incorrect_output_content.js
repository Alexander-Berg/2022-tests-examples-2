// author: abeille@
for (let order_idx = 0; order_idx < order_contexts.length; order_idx++) {
  let order = order_contexts[order_idx].search_from_request;
  let buffer_info = order.buffer_info;
  if (buffer_info === undefined) {
    traces.orders[order_idx].text = "no buffer_info";
    continue;
  }
  let application = order.order.user_agent;
  if (application === undefined) {
    traces.orders[order_idx].text = "no application";
    continue;
  }
  let k = 180;
  let a = 430;
  let b = 2.45;
  let c = 0.12;
  let constant = 6;
  if (application === "call_center" 
      || application === "7220_call_center" 
      || application === "arm_call_center" 
      || application === "kz_call_center" 
      || application === "redtaxi_call_center" 
      || application === "saturn_call_center" 
      || application === "vezet_call_center" 
      || application === "vezetmini_call_center") {
      a = 400;
      b = 4.0;
      c = 0.14;
      constant = 15;
    } else if (application === "agent_gepard") {
      a = 400;
      b = 4.2;
      c = 0.12;
      constant = 20;
    }
  let first_dispatch_run = buffer_info.first_dispatch_run;
  if (first_dispatch_run === undefined) {
    traces.orders[order_idx].text = `0 sec, retention score is ${k}`;
    continue;
  }
  let first_dispatch_run_ts = Date.parse(first_dispatch_run);
  if(Number.isNaN(first_dispatch_run_ts)) {
    traces.orders[order_idx].text = "first_dispatch_run_ts parse error";
    continue;
  }
  let now_ts = Date.now();
  let sec_in_buffer = (now_ts - first_dispatch_run_ts)/1000;
  let retention_score = k + a * Math.exp(- Math.exp(b - c * sec_in_buffer));
  if (sec_in_buffer <  (30 + constant)) {
    traces.orders[order_idx].text = `${sec_in_buffer} < (30 + ${constant})  sec, retention score is ${retention_score} = ${k} + ${a} * exp(- exp(${b} - ${c} * ${sec_in_buffer}))`;
  }  else {
    traces.orders[order_idx].text = 'too old order, no retention';
  }
}
