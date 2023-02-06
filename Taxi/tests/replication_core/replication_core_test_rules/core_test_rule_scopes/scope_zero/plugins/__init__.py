def _zero(value):
    return 0


CAST = {
    'zero': _zero,
}


def _value_pow2(doc):
    return doc['value'] ** 2


INPUT_TRANSFORM = {
    'value_pow2': _value_pow2,
}


def _add_old_value(doc):
    doc = doc.copy()
    doc['old_value'] = doc['value']
    yield doc


PREMAP = {
    'add_old_value': _add_old_value,
}
