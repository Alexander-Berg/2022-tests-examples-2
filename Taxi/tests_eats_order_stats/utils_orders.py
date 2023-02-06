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
        eater_id=None,
        device_id=None,
        card_id=None,
        group_by=None,
        filters=None,
        filters_not=None,
        timerange=None,
):
    request = {
        'identities': make_identities(
            phone_id=phone_id,
            yandex_uid=yandex_uid,
            eater_id=eater_id,
            device_id=device_id,
            card_id=card_id,
        ),
    }

    if group_by is not None:
        request['group_by'] = group_by

    if filters is not None:
        request['filters'] = filters

    if filters_not is not None:
        request['filters_not'] = filters_not

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


def set_next_gen_settings(
        taxi_config, next_gen_read_enabled=False, next_gen_write_enabled=False,
):
    taxi_config.set_values(
        {
            'EATS_ORDER_STATS_NEXT_GEN_SETTINGS': {
                'next_gen_write_enabled': next_gen_write_enabled,
                'next_gen_read_enabled': next_gen_read_enabled,
            },
        },
    )
