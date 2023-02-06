function stage(restriction, value) {
  let result_value = value
  let restriction_meta = {}
  if (typeof(restriction.min) === "number") {
    result_value = Math.max(restriction.min, value)
    restriction_meta.min = restriction.min;
  }
  if (typeof(restriction.max) === "number") {
    result_value = Math.min(restriction.max, value)
    restriction_meta.max = restriction.max;
  }
  return {
    value: result_value,
    meta: restriction_meta,
  }
}
