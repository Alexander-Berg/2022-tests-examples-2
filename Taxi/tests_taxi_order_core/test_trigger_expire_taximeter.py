import datetime

import bson
import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize('expire_type', ['taximeter', 'cargo_taximeter'])
async def test_expire_taximeter_run(
        stq, stq_runner, mockserver, mongodb, expire_type,
):
    @mockserver.handler('/order-core/internal/processing/v1/event/expire')
    def post_event(req):
        assert req.query['order_id'] == order_id
        assert 'due' not in req.query
        body = bson.BSON(req.get_data()).decode()
        update = body['extra_update']['$set']
        assert update == {
            'status': 'finished',
            'order.user_fraud': False,
            'order.status': 'finished',
            'order.taxi_status': 'expired',
            'order.status_updated': _NOW,
        }
        assert body['event_extra_payload'] == {'s': 'finished', 't': 'expired'}
        assert body['fields'] == []
        assert body['filter'] == {'processing.version': 3}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['taximeter', 'cargo_taximeter']]

    move_past = datetime.datetime(2020, 4, 13, 13, 4, 58)
    proc_update = {
        '$set': {
            'order.request.due': move_past,
            'order.status_updated': move_past,
        },
    }
    if expire_type == 'cargo_taximeter':
        proc_update['$set']['order.request.cargo_ref_id'] = 'some_ref'
    mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    # when run expire, do not reschedule
    assert not stq.process_trigger.times_called
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert expire_type not in proc.get('trigger', {}).get('s', {})

    assert post_event.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(
    CARGO_EXPIRATION_SETTINGS_BY_TARIFF={
        '__default__': {
            'expired_hard_timeout': 86400,
            'max_taximeter_inactivity_before_expire': 3600,
        },
    },
    EXPIRED_HARD_TIMEOUT=86400,
    MAX_TAXIMETER_INACTIVITY_BEFORE_EXPIRE=3600,
)
@pytest.mark.parametrize(
    'proc_update, expected_delay',
    [
        ({'$set': {'order.status': 'pending'}}, None),
        (None, 3599000),
        (  # max timepoint is status_updated
            {
                '$set': {
                    'order.status_updated': datetime.datetime(
                        2021, 4, 13, 13, 5, 58,
                    ),
                },
            },
            3659899,
        ),
        (  # expire by hard_timout
            {
                '$set': {
                    'order_info.lta': datetime.datetime(
                        2022, 4, 13, 13, 4, 58,
                    ),
                },
            },
            86399000,
        ),
    ],
)
@pytest.mark.parametrize('expire_type', ['taximeter', 'cargo_taximeter'])
async def test_expire_taximeter_eta(
        stq, stq_runner, mongodb, proc_update, expected_delay, expire_type,
):
    order_id = 'order_1'
    args = [order_id, ['taximeter', 'cargo_taximeter']]

    if expire_type == 'cargo_taximeter':
        if proc_update is None:
            proc_update = {'$set': {}}
        proc_update['$set']['order.request.cargo_ref_id'] = 'some_ref'
    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    if expected_delay is None:
        assert not stq.process_trigger.times_called
    else:
        next_call = stq.process_trigger.next_call()
        eta = _NOW + datetime.timedelta(milliseconds=expected_delay)
        assert next_call['eta'] == eta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert expire_type not in proc.get('trigger', {}).get('s', {})


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(
    CARGO_EXPIRATION_SETTINGS_BY_TARIFF={
        '__default__': {
            'expired_hard_timeout': 10000,
            'max_taximeter_inactivity_before_expire': 3600,
        },
        'cargo': {
            'expired_hard_timeout': 10000,
            'max_taximeter_inactivity_before_expire': 3000,
        },
    },
)
async def test_redefine_cargo_settings(stq, stq_runner, mongodb):
    order_id = 'order_1'
    args = [order_id, ['taximeter', 'cargo_taximeter']]

    mongodb.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.status_updated': datetime.datetime(
                    2021, 4, 13, 13, 5, 58,
                ),
                'order.request.cargo_ref_id': 'cargo_ref',
            },
        },
    )

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    next_call = stq.process_trigger.next_call()
    eta = _NOW + datetime.timedelta(milliseconds=3059899)
    assert next_call['eta'] == eta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'cargo_taximeter' not in proc.get('trigger', {}).get('s', {})
