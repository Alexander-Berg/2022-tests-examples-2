import six


# to ensure that input data presented exactly as it comes from Cluster
def to_bytes(val):
    if isinstance(val, str):
        return six.ensure_binary(val)
    elif isinstance(val, dict):
        return {to_bytes(k): to_bytes(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [to_bytes(i) for i in val]

    return val


def to_string(val):
    if isinstance(val, bytes):
        return six.ensure_str(val)
    elif isinstance(val, dict):
        return {to_string(k): to_string(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [to_string(i) for i in val]

    return val
