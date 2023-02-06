function stage(
    point_b,
    category,
    value_raw,
    max_jump_up,
    max_jump_down,
    default_smooth_surge_a,
    default_smooth_surge_b,
    value_smooth_a,
    value_smooth_b
) {
    const kDefaultSurgeValue = 1.0;

    let result = {
        smooth_a: {
            value: value_smooth_a || default_smooth_surge_a || kDefaultSurgeValue,
            is_default: !value_smooth_a,
        },
        smooth_b: point_b ? {
            value: value_smooth_b || default_smooth_surge_b || kDefaultSurgeValue,
            is_default: !value_smooth_b
        } : null
    };

    result.value = Math.max(
        Math.min(value_raw, result.smooth_a.value + max_jump_up),
        result.smooth_a.value - max_jump_down
    );

    return result;
}