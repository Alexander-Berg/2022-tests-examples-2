FILE = 'sub_set_extra.json'
ROUTE_SET_EXTRA = '/v1/subscriptions/set-extra'
ROUTE_GET_SUBS = '/v1/subscriptions'


async def test_update_subs_simple(
        make_tariffs_request, load_json, create_subs,
):
    subs = await create_subs('simple')
    assert len(subs) == 1
    sub_id = subs[0]['id']
    data = load_json(FILE)['valid']
    for task in data:
        task['request']['id'] = sub_id
        status = task['response']['status_code']
        await make_tariffs_request(
            ROUTE_SET_EXTRA,
            method='put',
            data=task['request'],
            status_code=status,
            headers={'X-Yandex-Login': 'some'},
        )
    subs = await make_tariffs_request(ROUTE_GET_SUBS, method='get')
    for sub in subs['subscriptions']:
        sub_by_id = await make_tariffs_request(
            ROUTE_GET_SUBS,
            method='get',
            params={'subscription_id': sub['id']},
        )
        assert len(sub_by_id['subscriptions']) == 1
        sub = sub_by_id['subscriptions'][0]
        assert 'tariff_name' in sub['extra']
