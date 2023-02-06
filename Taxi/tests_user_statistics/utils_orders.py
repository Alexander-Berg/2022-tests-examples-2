import copy


def make_identities(**kwargs):
    return [
        {'type': key, 'value': value}
        for key, value in kwargs.items()
        if value is not None
    ]


def make_filters(**kwargs):
    return [
        {'name': key, 'values': values}
        for key, values in kwargs.items()
        if values is not None
    ]


def make_request(
        phone_id=None,
        yandex_uid=None,
        card_persistent_id=None,
        device_id=None,
        group_by=None,
        filters=None,
        timerange=None,
):
    request = {
        'identities': make_identities(
            phone_id=phone_id,
            yandex_uid=yandex_uid,
            card_persistent_id=card_persistent_id,
            device_id=device_id,
        ),
    }

    if group_by is not None:
        request['group_by'] = group_by

    if filters is not None:
        request['filters'] = filters

    if timerange is not None:
        request['timerange'] = timerange

    return request


def get_sorted_response(response):
    result = copy.deepcopy(response)
    result['data'].sort(
        key=lambda item: item['identity']['type'] + item['identity']['value'],
    )

    for identity in result['data']:
        for counter in identity['counters']:
            counter['properties'].sort(
                key=lambda item: item['name'] + item['value'],
            )
        identity['counters'].sort(
            key=lambda item: ''.join(
                [p['name'] + p['value'] for p in item['properties']],
            ),
        )
    return result
