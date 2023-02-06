function stage(threshold, base_class, value, surcharge, point_b_smooth_is_default) {
    const has_actual_point_b_surge = point_b_smooth_is_default === false;

    function copy_object(object) {
        return Object.assign({}, object);
    }

    let result = {
        value: value,
        surcharge: surcharge,
        explicit_antisurge: null,
    };

    if (has_actual_point_b_surge) {
        result.explicit_antisurge = {
            value: value,
            // FIXME: surcharge object should be explicitly copied because
            //  its copying and changing is done in single stage.
            //  Otherwise out bindings order should be respected:
            //  first - copy, second - change
            surcharge: surcharge ? copy_object(surcharge) : null,
        };
    } else {
        log.info("Explicit antisurge: hidden only - no actual point b surge");
    }

    result.value = threshold;
    result.surcharge = null;

    return result;
}