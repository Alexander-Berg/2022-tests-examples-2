function stage(classes, point_a, tariff_zone, layer_meta) {
    function map_object_to_array(object, fn, fn_if) {
        let result = [];
        for (let key in object) {
            let item = object[key];
            if (typeof fn_if !== 'function' || fn_if(item)) {
                result.push(fn(item));
            }
        }
        return result;
    }

    let request = {
        allowed_classes: map_object_to_array(
            classes,
            info => info.name,
            info => info.calculation_meta.reason === "pins_free" || info.name === base_class
        ),
        limit: 400,
        max_distance: 2500,
        point: point_a,
    };

    if (tariff_zone) {
        request.zone_id = tariff_zone;
    }

    return {
        drivers_info: {
            layer_meta: layer_meta,
            request: request,
        }
    };
}