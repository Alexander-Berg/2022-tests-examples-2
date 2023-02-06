import datetime
import json

import pytest

SUB_ROUTE_YT = '/v1/subscriptions/create-yt-table'
SUB_ROUTE_INIT = '/v1/subscriptions/init'
FILE_NEW = 'sub_new.json'


@pytest.mark.parametrize(
    'expected_count, status', [(0, 200), (1, 201), (5, 201), (3, 201)],
)
async def test_save_to_yt(
        patch,
        web_app_client,
        mock_parks_replica,
        mock_billing_replication,
        make_tariffs_request,
        load_json,
        create_subs,
        _update_subs,
        expected_count,
        status,
):
    @patch('hiring_tariffs.internal.yt_operations.save_data_for_billing')
    async def _save_data_for_billing(*args, **kwargs):
        assert datetime.datetime.utcnow().strftime('%Y_%m_%dT%H_%M') in args[1]
        assert len(args[2]) == expected_count
        return

    await create_subs('multiple')
    await _update_subs(expected_count)
    response = await web_app_client.post(SUB_ROUTE_YT)
    assert response.status == status


@pytest.fixture
def _update_subs(pgsql, find_subs):
    async def _wrapper(expected_count):
        if not expected_count:
            return
        subs = await find_subs()
        now = datetime.datetime.utcnow()
        yesterday = (now - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        tomorrow = (now + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        extra = {'agglomeration': 'Msk1', 'park_id': 'PARK_ID', 'vat': 20}
        sub_id = subs[0]['id']
        result = _generate_update_for_one_sub(sub_id, now, yesterday, tomorrow)
        for sub in subs[1:expected_count]:
            result.append(
                {
                    'subscription_id': sub['id'],
                    'status': 'processing',
                    'starts_at': yesterday,
                    'ends_at': tomorrow,
                },
            )
        with pgsql['hiring_misc'].cursor() as cursor:
            cursor.execute(
                'INSERT INTO'
                '   "hiring_tariffs"."subscriptions_periods" ('
                '       subscription_id,'
                '       status,'
                '       starts_at,'
                '       ends_at'
                '   ) '
                'SELECT'
                '   subscription_id,'
                '   status,'
                '   starts_at,'
                '   ends_at '
                'FROM'
                '   jsonb_populate_recordset('
                '       null::"hiring_tariffs"."subscriptions_periods",'
                '       \'{result}\'::jsonb'
                ');'
                'UPDATE "hiring_tariffs"."subscriptions" '
                'SET extra = \'{extra}\'::JSONB'
                ';'.format(result=json.dumps(result), extra=json.dumps(extra)),
            )

        return result

    return _wrapper


def _generate_update_for_one_sub(
        sub_id: str, now: datetime.datetime, yesterday: str, tomorrow: str,
):
    result = [
        {
            'subscription_id': sub_id,
            'status': 'processing',
            'starts_at': (now - datetime.timedelta(days=3)).strftime(
                '%Y-%m-%d',
            ),
            'ends_at': yesterday,
        },
        {
            'subscription_id': sub_id,
            'status': 'processing',
            'starts_at': tomorrow,
            'ends_at': (now + datetime.timedelta(days=3)).strftime('%Y-%m-%d'),
        },
    ]
    for status in {'draft', 'active', 'rejected', 'completed', 'processing'}:
        result.append(
            {
                'subscription_id': sub_id,
                'status': status,
                'starts_at': yesterday,
                'ends_at': tomorrow,
            },
        )
    return result
