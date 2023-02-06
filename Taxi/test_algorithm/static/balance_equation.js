function stage(
    category,
    reason,
    surge_latest_pins_delta_time,
    base_class,
    surge_rules,
    min_pins,
    min_total,
    f_init,
    f_equal,
    f_delta_left,
    f_delta_right,
    add_free,
    add_total,
    fs_intercept,
    fs_coef_chain,
    fs_coef_total,
    chain_factor,
    reposition_discount,
    utilization_for_non_base,
    table_coef_ps,
    radius,
    counts,
    reposition_counts,
    base_class_counts,
    reposition_base_class_counts,
    surge_statistics,
    sample_dynamic_config,
    pins,
    pins_with_b,
    pins_with_order,
    pins_with_driver,
    prev_pins,
    pins_meta_by_category,
) {
    function require(value, description) {
        if (!is_present(value)) {
            throw 'no ' + description;
        }
    }

    function map_object(object, fn, fn_if) {
        let result = {}
        for (let key in object) {
            let item = object[key];
            if (typeof fn_if !== 'function' || fn_if(item)) {
                result[key] = (fn(item));
            }
        }
        return result;
    }

    function in_epsilon_neighborhood_of_zero(value) {
        return Math.abs(value) <= Number.EPSILON;
    }

    function get_category_specific_pin_meta(field_name, is_non_base) {
        if (is_non_base) {
            let result = {};
            if (category in pins_meta_by_category) {
                let meta = pins_meta_by_category[category];
                if (field_name in meta) {
                    result[category] = meta[field_name];
                }
            }
            return result;
        } else {
            return map_object(
                pins_meta_by_category,
                meta => meta[field_name],
                meta => field_name in meta,
            );
        }
    }

    chain_factor = chain_factor || 1.0;

    require(category, 'category name');
    require(pins, 'pins info');
    require(counts, category + 'counts');
    require(base_class_counts, 'base class counts');

    const kDefaultSurgeValue = 1.0;
    const kReasonNo = 'no';
    const kReasonPinsFree = 'pins_free';
    const kMessageNotActive = 'balance equation is not active: ';

    const is_non_base = category !== base_class;
    const is_utilization = utilization_for_non_base && is_non_base;

    const selected_counts = is_utilization ? counts : base_class_counts;
    const selected_reposition_counts = is_utilization ? reposition_counts : reposition_base_class_counts;

    let free = selected_counts.free;
    let free_chain = selected_counts.free_chain;
    let on_order = selected_counts.on_order;  // unused
    let total = selected_counts.total;

    let balance_log_info = {
        deviation_from_target_abs: 2.22,
        ps_shift_past_raw: 3.33
    }

    if (is_non_base) {
        balance_log_info = null;
    }

    // Доля свободных машин
    function get_ratio_balance() {
        let corrected_total = total + add_total;
        if (is_present(reposition_discount) && is_present(selected_reposition_counts)) {
            // https://st.yandex-team.ru/EFFICIENCYDEV-20
            corrected_total += reposition_discount * selected_reposition_counts.total;
        }
        if (in_epsilon_neighborhood_of_zero(corrected_total)) {
            return 0.0;
        }
        let corrected_free = free + chain_factor * free_chain + add_free;
        if (is_present(reposition_discount) && is_present(selected_reposition_counts)) {
            // https://st.yandex-team.ru/EFFICIENCYDEV-20
            corrected_free += reposition_discount *
                (selected_reposition_counts.free + chain_factor * selected_reposition_counts.free_chain);
        }
        return corrected_free / corrected_total;
    }

    function make_result(
        reason = kReasonNo,
        value_raw = kDefaultSurgeValue,
        ps = null,
        f_derivative = null,
    ) {
        const cat_meta = pins_meta_by_category[category] || {};

        let pins_meta = {
            pins_b: pins_with_b,
            pins_order: pins_with_order,
            pins_driver: pins_with_driver,
            prev_pins: prev_pins,
            eta_in_tariff: cat_meta.estimated_waiting || 0.0,
            surge_in_tariff: cat_meta.surge || 0.0,
            pins_order_in_tariff: cat_meta.pins_order_in_tariff || 0,
            pins_driver_in_tariff: cat_meta.pins_driver_in_tariff || 0,
        }
        if (is_present(cat_meta.cost)) {
            pins_meta.cost = cat_meta.cost;
        }
        if (is_present(cat_meta.surge_b)) {
            pins_meta.surge_b_in_tariff = cat_meta.surge_b;
        }
        if (is_present(cat_meta.trip)) {
            pins_meta.distance = cat_meta.trip.distance;
            pins_meta.time = cat_meta.trip.time;
        }
        if (is_present(cat_meta.pins_surge_b_percentiles)) {
            pins_meta.pins_surge_b_percentiles = cat_meta.pins_surge_b_percentiles;
        }

        let calculation_meta = {
            counts: {
                free: counts.free,
                free_chain: counts.free_chain,
                total: counts.total,
                pins: pins,
                radius: radius,
            },
            reason: reason,
            pins_meta: pins_meta,
        };

        if (is_present(reposition_counts)) {
            calculation_meta.reposition = {
                free: reposition_counts.free,
                free_chain: reposition_counts.free_chain,
                total: reposition_counts.total,
            };
        }

        if (is_present(ps)) {
            calculation_meta.ps = ps;
        }

        if (is_present(f_derivative)) {
            calculation_meta.f_derivative = f_derivative;
        }

        if (is_present(balance_log_info)) {
            calculation_meta.deviation_from_target_abs =
                balance_log_info.deviation_from_target_abs;
            calculation_meta.ps_shift_past_raw =
                balance_log_info.ps_shift_past_raw;
        }

        if (is_present(surge_statistics)) {
            if (calculation_meta.extra === undefined) {
                calculation_meta.extra = {};
            }
            calculation_meta.extra.surge_statistics = surge_statistics.results;
        }

        if (is_present(sample_dynamic_config)) {
            if (calculation_meta.extra === undefined) {
                calculation_meta.extra = {};
            }
            calculation_meta.extra.sample_dynamic_config = sample_dynamic_config;
        }

        return {
            value_raw: value_raw,
            calculation_meta: calculation_meta,
        };
    }

    function make_result_by_ratio(ratio) {
        let value_raw = kDefaultSurgeValue;
        for (let rule of surge_rules) {
            if (rule.min_coeff <= ratio) {
                value_raw = rule.surge_value;
            } else {
                break;
            }
        }
        return make_result(kReasonPinsFree, value_raw);
    }

    function make_result_by_ps(ps, f_derivative) {
        let reason = kReasonNo;
        let value_raw = kDefaultSurgeValue;

        let ps_deviation = undefined;
        for (let table_coef_item of table_coef_ps) {
            let current_ps_deviation = Math.abs(ps - table_coef_item.ps);
            if (!is_present(ps_deviation) || current_ps_deviation < ps_deviation) {
                reason = kReasonPinsFree;
                value_raw = table_coef_item.coeff;
                ps_deviation = current_ps_deviation;
            }
        }
        return make_result(reason, value_raw, ps, f_derivative);
    }

    const ratio = get_ratio_balance();
    // Утилизация считается по тому же ратио, но по правилам для класса
    // https://st.yandex-team.ru/TAXIBACKEND-6549
    if (is_utilization) {
        log.info(
            'balance enabled but utilization formula is active for ' + category
        );
        if (total < min_total) {
            log.info(
                kMessageNotActive + ': total{' + total +
                '} is less than min_total{' + min_total + '}'
            );
            return make_result();
        }
        return make_result_by_ratio(ratio);
    }
    // Порог, при котором не начинаем считать производную
    if (ratio >= f_init) {
        log.info(
            kMessageNotActive + ': ratio{' + ratio + '} >= f_init{' +
            f_init + '}');
        return make_result();
    }
    if (in_epsilon_neighborhood_of_zero(pins)) {
        log.info(kMessageNotActive + ': zero pins (or too close to zero)');
        return make_result();
    }
    const window_minutes = surge_latest_pins_delta_time / 60;
    // Формула уравнения баланса https://st.yandex-team.ru/TAXIBACKEND-7194:
    // где  новая скорость = (fs_intercept + fs_coef_chain * free_chain +
    // fs_coef_total * total) / window
    //
    // f_derivative * total = (fs_intercept +
    // fs_coef_chain * free_chain + fs_coef_total * total) / window - p(s) * pins
    // / window
    //
    // =>
    //
    // f_derivative * total * window = (fs_intercept + fs_coef_chain * free_chain
    // + fs_coef_total * total) - p(s) * pins
    //
    // p(s) * pins = (fs_intercept +
    // fs_coef_chain * free_chain + fs_coef_total * total)
    // - f_derivative * total * window
    //
    // p(s) = (fs_intercept + fs_coef_chain * free_chain + fs_coef_total *
    // total - f_derivative * total * window) / pins

    let f_delta =
        ratio < f_equal ? f_delta_left : f_delta_right;
    // UPD: https://st.yandex-team.ru/TAXIBACKEND-6474
    // ratio' = f_delta * (f_equal - ratio(t))
    let f_derivative = f_delta * (f_equal - ratio);
    if (is_present(reposition_discount) &&
        is_present(selected_reposition_counts)
    ) {
        // https://st.yandex-team.ru/EFFICIENCYDEV-20
        total += reposition_discount * selected_reposition_counts.total;
        free_chain += reposition_discount * selected_reposition_counts.free_chain;
    }

    let ps = (
        fs_intercept + fs_coef_chain * free_chain + total * fs_coef_total -
        f_derivative * total * window_minutes
    ) / pins;

    return make_result_by_ps(ps, f_derivative);
}
