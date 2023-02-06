function stage(classes, point_a, radius, layer_meta) {
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

    return {
        pins_info: {
            layer_meta: layer_meta,
            request: {
                categories: map_object_to_array(
                    classes,
                    info => info.name,
                    info => info.calculation_meta.reason === "pins_free"
                ),
                point: point_a,
                radius: radius,
                high_surge_b: [50, 70, 95, 98]
            }
        }
    };
}
