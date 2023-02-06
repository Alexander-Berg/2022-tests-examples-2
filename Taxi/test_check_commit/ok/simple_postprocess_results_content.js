for (let order_idx = 0; order_idx < order_contexts.length; order_idx++) {
  let order = order_contexts[order_idx];
  let candidates = candidates_contexts[order_idx];
  var scored_order = scoring_results.orders[order_idx];
  for (let cand_idx = 0; cand_idx < candidates.length; cand_idx++) {
      scored_order.candidates[cand_idx].score = 2
  }
  scoring_results.orders[order_idx].retention_score = 1;
}
