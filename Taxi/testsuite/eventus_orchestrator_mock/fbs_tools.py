def make_fbs_string(builder, object_raw):
    return builder.CreateString(object_raw)


def make_fbs_vector_via_func(
        builder, objects_raw, func, start_vector, prepend_func=None,
):
    objects_list = [func(builder, object) for object in reversed(objects_raw)]
    start_vector(builder, len(objects_list))
    for obj in objects_list:
        if prepend_func is not None:
            prepend_func(obj)
        else:
            builder.PrependUOffsetTRelative(obj)
    return builder.EndVector(len(objects_list))
