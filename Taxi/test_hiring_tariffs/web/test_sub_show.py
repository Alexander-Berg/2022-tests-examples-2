import json
import typing

import pytest


FILE_SHOW = 'sub_show.json'
SHOW = '/v1/subscriptions'


@pytest.fixture
def update_subs(pgsql):
    async def _wrapper(updates, periods):
        with pgsql['hiring_misc'].cursor() as cursor:
            cursor.execute(
                'INSERT INTO hiring_tariffs.subscriptions_periods ('
                '"subscription_id",'
                '"status",'
                '"starts_at",'
                '"ends_at"'
                ')'
                'SELECT'
                '   t.subscription_id,'
                '   t.status,'
                '   t.starts_at,'
                '   t.ends_at '
                'FROM jsonb_populate_recordset('
                '   null::hiring_tariffs.subscriptions_periods,'
                '   \'{periods}\'::jsonb'
                ') AS t'
                ';'
                'INSERT INTO hiring_tariffs.subscriptions_updates ('
                '"subscription_id",'
                '"data",'
                '"author",'
                '"comment"'
                ')'
                'SELECT'
                '   v.subscription_id,'
                '   v.data,'
                '   v.author,'
                '   v.comment '
                'FROM jsonb_populate_recordset('
                '   null::hiring_tariffs.subscriptions_updates,'
                '   \'{updates}\'::jsonb'
                ') AS v'
                ';'.format(
                    periods=json.dumps(periods), updates=json.dumps(updates),
                ),
            )

    return _wrapper


async def _prepare_updates_and_periods(subs: typing.List[dict]):
    updates = []
    periods = []
    for sub in subs:
        updates.append(
            {
                'subscription_id': sub['id'],
                'data': {'starts_at': '2020-10-1'},
                'author': sub['subscriber_id'],
                'comment': 'some comment',
            },
        )
        periods.append(
            {
                'subscription_id': sub['id'],
                'status': sub['subscriber_id'],
                'starts_at': '2020-10-1',
                'ends_at': '2020-10-30',
            },
        )
    return updates, periods


async def _prepare_params(request: dict, subs):
    if not request:
        return {}
    if 'subscription_id' in request and not request['subscription_id']:
        request['subscription_id'] = subs[0]['id']
    return request


async def _check_response(sub: dict, params: dict):
    assert len(sub['updates']) == 2
    for key, value in params.items():
        if key == 'subscription_id':
            assert sub['id'] == value
        elif key == 'subscriber_id':
            assert sub['subscriber_id'] == value
        else:
            for period in sub['periods']:
                if key == 'status':
                    assert period[key] == value
                elif key == 'starts_at':
                    assert period[key] >= value
                else:
                    assert period[key] <= value


async def _check_subscriber_id(sub: dict, params: dict):
    assert sub['subscriber_id'] == params['subscriber_id']


@pytest.mark.usefixtures('sub_suggests_fill')
@pytest.mark.parametrize(
    'case',
    [
        'all',
        'by_id',
        'by_subscriber_id',
        'by_status',
        'by_starts_at',
        'by_ends_at',
        'no_subs',
    ],
)
async def test_show_subs_simple(
        make_tariffs_request,
        load_json,
        create_subs,
        update_subs,  # pylint: disable=W0621,R1710
        case,
):
    subs = await create_subs('multiple')
    assert len(subs) == 5
    updates, periods = await _prepare_updates_and_periods(subs)
    await update_subs(updates, periods)
    data = load_json(FILE_SHOW)['valid'][case]
    for task in data:
        status = task['response']['status_code']
        params = await _prepare_params(task['request'], subs)
        response = await make_tariffs_request(
            SHOW, method='get', status_code=status, params=params,
        )
        if status != 200:
            assert task['response']['body']['code'] == response['code']
            continue
        subs = response['subscriptions']
        if case == 'no_subs':
            assert not subs
            continue
        assert subs
        for sub in subs:
            await _check_response(sub, params)


async def test_show_by_subscriber_id(
        make_tariffs_request, load_json, create_subs,
):
    await create_subs('multiple')
    data = load_json(FILE_SHOW)['valid']['with_limit']
    for task in data:
        params = task['request']
        response = await make_tariffs_request(
            SHOW, method='get', params=params,
        )
        subs = response['subscriptions']
        assert subs
        for sub in subs:
            await _check_subscriber_id(sub, params)
