function stage(
    point_b,
    zone_id,
    default_smooth_surge_a,
    default_smooth_surge_b,
    use_default_surge_if_no_smoothing,
    category,
    value_raw
) {
    const kDefaultSurgeValue = 1.0;
    const default_a = default_smooth_surge_a || kDefaultSurgeValue;
    const default_b = default_smooth_surge_b || kDefaultSurgeValue;

    return {
        smooth_a: {
            is_default: true,
            value: default_a,
        },
        smooth_b: point_b ? {
            is_default: true,
            value: default_b,
        } : null,
        value: use_default_surge_if_no_smoothing ? default_a : value_raw,
    };
}