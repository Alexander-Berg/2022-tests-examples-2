function stage(classes) {
  for (let class_info of Object.values(classes)) {
    if (class_info.calculation_meta.reason === 'pins_free') return true;
  }
  return false;
}
