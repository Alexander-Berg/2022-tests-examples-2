from testsuite.utils import matching


def operator_match(item, context):
    if not context.allow_matching:
        raise RuntimeError('Matching is not allowed here')
    if isinstance(item, str):
        return _operator_match({'type': item}, context)
    return _operator_match(item, context)


def _operator_match(doc: dict, context):
    match_type = doc['type']
    if match_type == 'any-string':
        return matching.any_string
    if match_type == 'uuid-string':
        return matching.uuid_string
    if match_type == 'objectid-string':
        return matching.objectid_string
    if match_type == 'regex':
        return matching.RegexString(doc['pattern'])
    raise RuntimeError(f'Unknown match type {match_type}')
