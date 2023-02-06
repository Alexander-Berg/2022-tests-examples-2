function stage(idx, category, value, surge_min_bound, surge_max_bound) {
    function value_or_number(value, default_value) {
        return typeof value === 'number' ? value : default_value;
    }

    let min_surge = value_or_number(surge_min_bound, 1.0);
    let max_surge = value_or_number(surge_max_bound, 4.0);

    return {
        value: Math.max(Math.min(value, max_surge), min_surge)
    };
}