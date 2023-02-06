function stage(
    category,
    reason,
    from_class,
    surge_linear_coeff,
    from_class_value_raw,
    from_class_value,
    from_class_smooth
) {
    function require(value, description) {
        if (!is_present(value)) {
            throw 'no ' + description;
        }
    }

    const kDefaultSurgeValue = 1.0;

    require(category, "category");
    require(from_class, "from_class");
    require(surge_linear_coeff, "linear_coeff");
    require(from_class_value_raw, "from_class_value_raw");
    require(from_class_value, "from_class_value");
    require(from_class_smooth, "from_class_smooth");

    if (category === from_class) {
        throw "Impossible to apply linear dependency from itself";
    }

    return {
        value_raw: from_class_value_raw,
        value: kDefaultSurgeValue + surge_linear_coeff * (from_class_value - kDefaultSurgeValue),
        smooth: from_class_smooth,
    };
}
