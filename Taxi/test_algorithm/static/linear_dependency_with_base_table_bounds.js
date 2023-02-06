function stage(category, value, use_base_class_table, surge_min_bound, surge_max_bound) {
    return {value: Math.max(Math.min(value, surge_max_bound), surge_min_bound)};
}