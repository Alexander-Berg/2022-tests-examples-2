import json

ENOUGH_NUMDOCS = 10


def numdocs(dump):
    _numdocs = int(dump['searchdata']['numdocs'])
    return {'numdocs': _numdocs, 'has_docs': _numdocs > 0, 'has_enough_docs': _numdocs >= ENOUGH_NUMDOCS}


def direct(dump):
    props = dump['search_props']['UPPER'][0]['properties']
    has_direct_keys = [
        'Banner.has_direct_dynamic',
        'Banner.has_direct_guarantee',
        'Banner.has_direct_halfpremium',
        'Banner.has_direct_media',
        'Banner.has_direct_premium',
    ]
    direct_count_keys = [
        'Banner.direct_halfpremium_count',
        'Banner.direct_premium_count',
    ]
    result = {'has_direct': any(int(props.get(key, 0)) for key in has_direct_keys)}
    result.update({key: int(props.get(key, 0)) for key in direct_count_keys})
    return result


def query(dump):
    return {'query': dump['search']['text']['text']}


def json_dump(dump):  # only for manual testing - it increases parsing time and output table size dramatically
    return {'dump': json.dumps(dump)}
