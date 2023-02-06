import datetime
import typing

import pytest


FILE_UPDATE = 'sub_update.json'
ROUTE_UPDATE = '/v1/subscriptions/update'


@pytest.mark.parametrize('case', ['simple', 'multiple_fields'])
async def test_update_subs_simple(
        make_tariffs_request,
        mock_approvals,
        load_json,
        create_subs,
        pgsql,
        case,
):
    subs = await create_subs('simple')
    assert len(subs) == 1
    sub_id = subs[0]['id']
    with pgsql['hiring_misc'].cursor() as cursor:
        cursor.execute(
            'UPDATE hiring_tariffs.subscriptions_periods '
            'SET status = \'active\' '
            'WHERE subscription_id = \'{sub_id}\';'
            'INSERT INTO hiring_tariffs.subscriptions_periods ('
            '   "subscription_id",'
            '   "status",'
            '   "starts_at",'
            '   "ends_at"'
            ')'
            'VALUES ('
            '   \'{sub_id}\','
            '   \'completed\','
            '   \'2020-10-1\'::DATE,'
            '   \'2020-10-30\'::DATE'
            ');'.format(sub_id=sub_id),
        )
    data = load_json(FILE_UPDATE)['valid'][case]
    for task in data:
        request_body = await _prepare_request(task, sub_id)
        expected = task['response']
        status = expected['status_code']
        if expected['body']['code'] == 'NO_ACTIVE_PERIODS':
            with pgsql['hiring_misc'].cursor() as cursor:
                cursor.execute(
                    'UPDATE hiring_tariffs.subscriptions_periods '
                    'SET status = \'processing\' '
                    'WHERE subscription_id = \'{sub_id}\';'.format(
                        sub_id=sub_id,
                    ),
                )
        response = await make_tariffs_request(
            ROUTE_UPDATE,
            method='put',
            data=request_body,
            status_code=status,
            headers={'X-Yandex-Login': 'some'},
        )
        if status == 400:
            assert expected['body']['code'] == response['code']
            continue
        if status == 200:
            assert response['draft_id'] == 0
        else:
            assert response['draft_id'] != 0


async def _prepare_request(task: dict, sub_id: str) -> dict:
    task['request']['subscription_id'] = sub_id
    if 'starts_at' in task['request'] and not task['request']['starts_at']:
        now = datetime.datetime.utcnow()
        task['request']['starts_at'] = (
            now + datetime.timedelta(days=2)
        ).strftime('%Y-%m-%d')
    return task['request']


async def _check_updates(
        subs: typing.List[dict],
        updated_subs: typing.List[dict],
        task: dict,
        updates: int,
):
    assert len(updated_subs) == 1
    assert task['response']['body'].items() <= updated_subs[0].items()
    assert len(updated_subs[0]['periods']) == 2
    assert len(updated_subs[0]['updates']) == updates
    if 'starts_at' in task['request']:
        active_period = next(
            (
                period
                for period in updated_subs[0]['periods']
                if period['status']
                in ['active', task['request'].get('status')]
            ),
            None,
        )
        assert active_period
        old_starts_at = subs[0]['periods'][0]['starts_at']
        assert old_starts_at != active_period['starts_at']
    if 'status' in task['request']:
        for period in updated_subs[0]['periods']:
            assert period['status'] in ['completed', task['request']['status']]
