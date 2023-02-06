import collections

SelectParameters = collections.namedtuple(
    'SelectParameters',
    [
        'rule_types',
        'tags',
        'tariff_classes',
        'zones',
        'geoareas',
        'unique_driver_id',
        'branding',
    ],
)


def make_hashable(lst):
    if lst is None:
        return None
    if isinstance(lst, bool):
        return lst
    return tuple(sorted(lst))


def extract_select_params(request_body):
    rule_types = request_body['rule_types']

    if 'tags_constraint' in request_body:
        if 'tags' in request_body['tags_constraint']:
            tags = request_body['tags_constraint']['tags']
        else:
            tags = request_body['tags_constraint']['has_tag']
    else:
        tags = None

    if 'geoareas_constraint' in request_body:
        if 'geoareas' in request_body['geoareas_constraint']:
            geoareas = request_body['geoareas_constraint']['geoareas']
        else:
            geoareas = request_body['geoareas_constraint']['has_geoarea']
    else:
        geoareas = None

    tariff_classes = request_body.get('tariff_classes', None)

    zones = request_body.get('zones', None)

    unique_driver_id = request_body.get('drivers', None)

    branding = request_body.get('branding', None)

    return SelectParameters(
        make_hashable(rule_types),
        make_hashable(tags),
        make_hashable(tariff_classes),
        make_hashable(zones),
        make_hashable(geoareas),
        make_hashable(unique_driver_id),
        make_hashable(branding),
    )
