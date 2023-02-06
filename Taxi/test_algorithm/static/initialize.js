function stage(category, fixed_surge_value, fixed_reason, time_rules, linear_dependency_enabled, balance) {
    if (linear_dependency_enabled) {
        return {
            class_info: {
                name: category,
                surge: {
                    value: 1.0,
                },
                value_raw: 1.0,
                calculation_meta: {
                    reason: "linear_dependency",
                },
            },
        };
    }

    if (fixed_surge_value) {
        return {
            class_info: {
                name: category,
                surge: {
                    value: 1.0,
                },
                value_raw: fixed_surge_value,
                calculation_meta: {
                    reason: fixed_reason || "no",
                },
            },
        };
    }

    if (time_rules) {
        const now = new Date();
        const hour_now = (now.getUTCHours() + 3) % 24; // Moscow +3
        const mins_now = now.getMinutes();
        for (let time_rule of time_rules) {
            const hour_from = time_rule.time_from.hour;
            const mins_from = time_rule.time_from.minute;
            const hour_to = time_rule.time_to.hour;
            const mins_to = time_rule.time_to.minute;

            const gt_from = hour_now > hour_from || (hour_now == hour_from && mins_now >= mins_from);
            const lt_to = hour_now < hour_to || (hour_now == hour_to && mins_now <= mins_to);

            if (gt_from && lt_to) {
                if (time_rule.surge_value) {
                    return {
                        class_info: {
                            name: category,
                            surge: {
                                value: 1.0,
                            },
                            value_raw: time_rule.surge_value,
                            calculation_meta: {
                                reason: "time",
                            },
                        },
                    };
                } else if (balance) {
                    return {
                        class_info: {
                            name: category,
                            surge: {
                                value: 1.0,
                            },
                            value_raw: 1.0,
                            calculation_meta: {
                                reason: "pins_free",
                            },
                        },
                    };
                } else {
                    log.info("balance not active: no params");
                    break;
                }
            }
        }
    }

    return {
        class_info: {
            name: category,
            surge: {
                value: 1.0,
            },
            value_raw: 1.0,
            calculation_meta: {
                reason: "no",
            },
        },
    };
}
