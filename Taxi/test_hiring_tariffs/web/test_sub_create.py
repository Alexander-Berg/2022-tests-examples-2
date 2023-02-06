import datetime

import pytest

FILE = 'sub_new.json'
ROUTE_INIT = '/v1/subscriptions/init'
ROUTE_SHOW = '/v1/subscriptions'


@pytest.mark.usefixtures('sub_suggests_fill')
async def test_create_subs_simple(make_tariffs_request, load_json):
    data = load_json(FILE)['valid']['simple_and_double']
    for task in data:
        status = task['response']['status_code']
        response = await make_tariffs_request(
            ROUTE_INIT,
            method='post',
            data=task['request'],
            status_code=status,
        )
        if status != 200:
            assert task['response']['body']['code'] == response['code']
            continue

        subs = response['subscriptions']
        assert len(subs) == 1
        assert task['response']['body'].items() <= subs[0].items()
        assert len(subs[0]['periods']) == 1
        starts_at = subs[0]['periods'][0]['starts_at']
        assert starts_at == datetime.datetime.now().strftime('%Y-%m-%d')


@pytest.mark.usefixtures('sub_suggests_fill')
@pytest.mark.parametrize(
    'autoprolong, status', [(False, 'created'), (False, 'draft')],
)
async def test_add_sub_period(
        make_tariffs_request, load_json, pgsql, autoprolong, status,
):
    data = load_json(FILE)['valid']['add_period']
    task = data[0]
    response = await make_tariffs_request(
        ROUTE_INIT, method='post', data=task['request'],
    )
    sub_id = response['subscriptions'][0]['id']
    with pgsql['hiring_misc'].cursor() as cursor:
        cursor.execute(
            'UPDATE hiring_tariffs.subscriptions_periods '
            'SET status = \'{status}\' '
            'WHERE subscription_id = \'{sub_id}\';'
            'UPDATE hiring_tariffs.subscriptions '
            'SET autoprolong = {autoprolong} '
            'WHERE id = \'{sub_id}\' '
            ';'.format(
                status=status,
                sub_id=sub_id,
                autoprolong='FALSE' if autoprolong is False else 'TRUE',
            ),
        )
    if autoprolong is True or status == 'created':
        response = await make_tariffs_request(
            ROUTE_INIT, method='post', data=task['request'], status_code=400,
        )
        assert task['response']['body']['code'] == response['code']
        return
    response = await make_tariffs_request(
        ROUTE_INIT, method='post', data=task['request'],
    )
    subs = response['subscriptions']
    assert len(subs) == 1
    periods = subs[0]['periods']
    assert len(periods) == 2
    assert periods[0]['starts_at'] > periods[1]['starts_at']


@pytest.mark.usefixtures('sub_suggests_fill')
async def test_reinit_subs(create_subs, pgsql, make_tariffs_request):
    await create_subs('simple')
    with pgsql['hiring_misc'].cursor() as cursor:
        cursor.execute(
            'UPDATE hiring_tariffs.subscriptions_periods '
            'SET status = \'rejected\' '
            ';',
        )
    await create_subs('simple')
    response = await make_tariffs_request(ROUTE_SHOW, method='get')
    subs = response['subscriptions']
    assert len(subs) == 1
    assert len(subs[0]['periods']) == 2
