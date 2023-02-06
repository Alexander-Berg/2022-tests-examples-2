function stage(point_a, classes, layer_meta) {
    function map_object_to_array(object, fn, fn_if) {
        let result = [];
        for (let value of Object.values(object)) {
            if (typeof fn_if !== 'function' || fn_if(value)) {
                result.push(fn(value));
            }
        }
        return result;
    }

    return {
        point_a_smoothing_info: {
            point: point_a,
            layer_meta: layer_meta,
            categories: map_object_to_array(classes, info => info.name),
        }
    }
}