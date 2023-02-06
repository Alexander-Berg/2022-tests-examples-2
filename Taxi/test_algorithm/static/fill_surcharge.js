function stage(base_class, rules, table_coef_ps, category, value) {
    const kDefaultSurge = 1.0;
    const kDefaultSurcharge = {
        alpha: 1.0,
        beta: 0.0,
        value: 0.0,
    };

    Object.freeze(kDefaultSurcharge);

    function is_number(value) {
        return typeof value === 'number';
    }

    function find_closest(iterable, get_deviation) {
        let selected_item = undefined;
        let deviation = undefined;
        for (let item of iterable) {
            let current_deviation = Math.abs(get_deviation(item));
            if (!is_present(deviation) || current_deviation < deviation) {
                selected_item = item;
                deviation = current_deviation;
            }
        }
        return selected_item;
    }

    let seen_categories = new Set();

    function get_surcharge_and_surge(current_category, recursive) {
        seen_categories.add(current_category);

        if (current_category === base_class) {
            if (is_present(table_coef_ps)) {
                let selected_table_coef_item = find_closest(table_coef_ps, item => item.coeff - value);
                if (selected_table_coef_item) {
                    return {
                        value: selected_table_coef_item.coeff,
                        surcharge: {
                            alpha: selected_table_coef_item.alpha,
                            beta: selected_table_coef_item.beta,
                            value: selected_table_coef_item.surcharge,
                        }
                    };
                }
            }
        } else {
            let rule = rules[current_category];
            if (rule) {
                if (recursive) {
                    let linear_dependency = rule.linear_dependency_formula;
                    if (linear_dependency && linear_dependency.use_base_class_table) {
                        // https://st.yandex-team.ru/EFFICIENCYDEV-3719
                        if (linear_dependency.from_class !== base_class || value >= kDefaultSurge) {
                            if (seen_categories.has(linear_dependency.from_class)) {
                                log.error("cyclic linear dependency: rerunning with disabled recursive table lookup");
                                // degradation: get first seen category and
                                // rerun function with recursive table lookup disabled
                                return get_surcharge_and_surge(seen_categories.values().next().value, /*recursive=*/false);
                            }
                            return get_surcharge_and_surge(linear_dependency.from_class, recursive);
                        }
                    }
                }

                let selected_surge_rules_item = find_closest(rule.surge_rules, item => item.surge_value - value);
                if (selected_surge_rules_item) {
                    return {
                        value: selected_surge_rules_item.surge_value,
                        surcharge: {
                            alpha: selected_surge_rules_item.alpha,
                            beta: selected_surge_rules_item.beta,
                            value: selected_surge_rules_item.surcharge,
                        }
                    };
                }
            }
        }

        return { value: value, surcharge: kDefaultSurcharge };
    }

    let result = get_surcharge_and_surge(category, /*recursive=*/true);

    if (!is_number(result.value)) {
        log.error('no surge value! default surcharge will be used');
        return { value: value, surcharge: kDefaultSurcharge };
    }

    let surcharge_coeffs = Object.values(result.surcharge);

    if (!surcharge_coeffs.some(is_number)) {
        // no surcharge params at all - use default but keep value from table
        result.surcharge = kDefaultSurcharge;
    } else if (!surcharge_coeffs.every(is_number)) {
        // incomplete surcharge params - considered ill formed - discard table
        log.warning('inconsistent surcharge params! default surcharge will be used');
        return { value: value, surcharge: kDefaultSurcharge };
    }

    return result;
}
