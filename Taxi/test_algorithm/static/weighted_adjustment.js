function stage(base_class, base_value, category, dep_value_raw, dep_total, enabled, settings) {
    function require_setting(name) {
        if (!(name in settings)) {
            throw name + ' is not present in settings';
        }
    }

    require_setting('min_adjustment_coeff');
    require_setting('max_adjustment_coeff');

    let weight_function = (x) => 1 / (1 + x);
    let bound_weight = (x, l, r) => l + (r - l) * weight_function(x);
    let adjusted_surge = (raw, coeff, base) => raw + coeff * (base - raw);

    return {
        value: adjusted_surge(
            dep_value_raw,
            bound_weight(
                dep_total,
                settings.min_adjustment_coeff,
                settings.max_adjustment_coeff),
            base_value),
    };
}
