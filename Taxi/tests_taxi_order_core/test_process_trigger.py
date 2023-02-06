import datetime

import bson
import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')

# triggers surgeprice and expire (taximeter/cargo_taximeter)
# can be available simultaneously


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'should_expire, proc_update, next_eta_delta',
    [
        # run surgeprice, it is nearest to reschedule
        (False, None, 60000),
        # run surgeprice, expire is nearest to reschedule
        (False, datetime.datetime(2021, 4, 13, 12, 55, 58, 101), 59899),
        # run surgeprcie and expire
        (True, datetime.datetime(2021, 4, 13, 12, 4, 0), 60000),
    ],
)
@pytest.mark.parametrize(
    'triggers_in_args',
    [
        ['surgeprice', 'seentimeout', 'search_expire', 'make_me_coffee'],
        pytest.param(
            ['surgeprice', 'seentimeout'],
            marks=[
                pytest.mark.config(
                    ORDER_CORE_ENABLED_TRIGGERS=[
                        'search_expire',
                        'make_me_coffee',
                    ],
                ),
            ],
        ),
        pytest.param(
            None,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_ENABLED_TRIGGERS=[
                        'surgeprice',
                        'seentimeout',
                        'search_expire',
                        'make_me_coffee',
                    ],
                ),
            ],
        ),
        pytest.param(
            ['seentimeout', 'search_expire', 'make_me_coffee'],
            marks=[
                pytest.mark.config(
                    ORDER_CORE_ENABLED_TRIGGERS=['surgeprice', 'seentimeout'],
                ),
            ],
        ),
    ],
)
async def test_process_trigger_happy_path(
        stq,
        stq_runner,
        mockserver,
        mongodb,
        should_expire,
        proc_update,
        next_eta_delta,
        triggers_in_args,
):
    @mockserver.handler('/order-core/internal/processing/v1/event/expire')
    def expire(req):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    update = {'$unset': {'performer': True, 'trigger': True}}
    if proc_update is not None:
        update['$set'] = {
            'order.request.due': proc_update,
            'order.created': proc_update,
            'created': proc_update,
            'order_info.statistics.status_updates.0.c': proc_update,
        }
    mongodb.order_proc.update({'_id': order_id}, update)
    # ignore unknown trigger

    args = [order_id, triggers_in_args]

    await stq_runner.process_trigger.call(task_id=order_id, args=args)

    next_call = stq.process_trigger.next_call()
    assert next_call['id'] == order_id
    # due to rescheduling we do not specify args
    assert next_call['args'] is None
    delta = datetime.timedelta(milliseconds=next_eta_delta)
    assert next_call['eta'] == _NOW + delta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['updated'] >= _NOW

    # update last_called for called trigger
    assert proc['trigger']['s']['surgeprice']['last_called'] == _NOW
    assert 'search_expire' not in proc.get('trigger', {}).get('s', {})
    assert 'seentimeout' not in proc.get('trigger', {}).get('s', {})

    assert expire.times_called == (1 if should_expire else 0)


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(
    DA_SEEN_TIMEOUT_DEFAULT=4,
    DA_SEEN_TIMEOUT_EXTRA=3,
    DA_SEEN_TIMEOUT_BY_TARIFF_EXTRA={'__default__': 10},
)
async def test_process_trigger_first_call(
        stq, stq_runner, mongodb, mockserver,
):
    # really, it should be lookupinit
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/seen_timeout',
    )
    def post_event(req):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['seentimeout', 'make_me_coffee']]
    ost = _NOW - datetime.timedelta(minutes=1)
    mongodb.order_proc.update(
        {'_id': order_id},
        {
            '$set': {'candidates.1.ost': ost, 'order.status': 'pending'},
            '$unset': {'trigger': ''},
        },
    )

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    assert not stq.process_trigger.times_called  # seentimeout not reschedule
    assert post_event.times_called == 1

    # trigger state not appeared
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'seentimeout' not in proc.get('trigger', {}).get('s', {})


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_trigger_no_etas(stq, stq_runner, mongodb):
    # no mocks because no triggers to run

    order_id = 'order_1'
    args = [order_id, ['search_expire', 'seentimeout', 'make_me_coffee']]

    # wrong status for both triggers
    mongodb.order_proc.update(
        {'_id': order_id}, {'$set': {'order.status': 'finished'}},
    )

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    assert not stq.process_trigger.times_called

    # last_called not updated
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'search_expire' not in proc.get('trigger', {}).get('s', {})
    assert 'seentimeout' not in proc.get('trigger', {}).get('s', {})


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_trigger_all_too_early(stq, stq_runner, mongodb):
    # no mocks because no triggers to run, just reschedule

    order_id = 'order_1'
    args = [order_id, ['surgeprice', 'seentimeout', 'make_me_coffee']]

    mongodb.order_proc.update(
        {'_id': order_id},
        {
            '$set': {'trigger.s.surgeprice.last_called': _NOW},
            '$unset': {'performer': True},
        },
    )

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    next_call = stq.process_trigger.next_call()
    assert next_call['id'] == order_id
    assert next_call['eta'] == _NOW + datetime.timedelta(seconds=60)

    # last_called not updated
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['trigger']['s']['surgeprice']['last_called'] == _NOW
    assert 'seentimeout' not in proc.get('trigger', {}).get('s', {})


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(MAX_TAXIMETER_INACTIVITY_BEFORE_EXPIRE=3600)
async def test_process_trigger_error_in_one_trigger(
        stq, stq_runner, mongodb, mockserver,
):
    @mockserver.handler('/order-core/internal/processing/v1/event/expire')
    def expire(req):
        return mockserver.make_response(
            status=500,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['search_expire', 'surgeprice', 'make_me_coffee']]

    move_past = datetime.datetime(2020, 4, 13, 13, 4, 58)
    mongodb.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.due': move_past,
                'order.created': move_past,
                'created': move_past,
                'order_info.statistics.status_updates.0.c': move_past,
            },
        },
    )

    await stq_runner.process_trigger.call(
        task_id=order_id, args=args, expect_fail=True,
    )
    assert not stq.process_trigger.times_called

    proc = mongodb.order_proc.find_one({'_id': order_id})
    # search_expire state does not changed
    assert expire.times_called == 1
    assert 'search_expire' not in proc.get('trigger', {}).get('s', {})
    # meanwhile surgeprice run with success
    assert proc['trigger']['s']['surgeprice']['last_called'] == _NOW


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'order_id, fail', [('order_exists', False), ('order_not_found', True)],
)
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
async def test_process_trigger_order_from_archive(
        stq, stq_runner, mockserver, mongodb, load_json, order_id, fail,
):
    archived_data = {i['_id']: i for i in load_json('archived_data.json')}

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    async def order_proc_restore(request):
        assert order_id == request.json['id']
        assert request.json.get('update', False)

        archived = archived_data.get(order_id)
        if not archived:
            return [{'id': order_id, 'status': 'not_found'}]

        mongodb.order_proc.insert(archived)
        return [{'id': order_id, 'status': 'restored'}]

    args = [order_id, ['taximeter', 'make_me_coffee']]

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    assert order_proc_restore.times_called == 1

    if fail:
        assert mongodb.order_proc.find_one({'_id': order_id}) is None
        assert stq.is_empty
    else:
        next_call = stq.process_trigger.next_call()
        assert next_call['id'] == order_id
        delta = datetime.timedelta(milliseconds=3599000)
        assert next_call['eta'] == _NOW + delta
