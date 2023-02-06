import datetime

import bson
import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_offer_timeout_run(stq, stq_runner, mockserver, mongodb):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/offer_timeout',
    )
    def post_event(req):
        assert req.query['order_id'] == order_id
        assert 'due' not in req.query
        body = bson.BSON(req.get_data()).decode()
        new_performer = body['extra_update']['$set'].pop('performer')
        assert new_performer == {
            'candidate_index': None,
            'need_sync': False,
            'presetcar': False,
            'alias_id': None,
            'driver_id': None,
            'park_id': None,
        }
        body_set = body['extra_update']['$set']
        assert body_set == {'lookup.state': {}, 'lookup.need_start': True}
        assert body['event_extra_payload'] == {'i': 1}
        assert body['fields'] == []
        assert body['filter'] == {'processing.version': 3}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['offertimeout']]

    with stq.flushing():
        await stq_runner.process_trigger.call(task_id=order_id, args=args)
        # when run offer-timeout, do not reschedule
        assert not stq.process_trigger.times_called
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'offertimeout' not in proc.get('trigger', {}).get('s', {})

    assert post_event.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(
    DA_OFFER_TIMEOUT_BY_TAGS={'deadman': 150, 'q': 110},
    DA_OFFER_TIMEOUT_EXTRA=4,
    DA_OFFER_TIMEOUT_BY_TARIFF={
        '__default__': {'__default__': 100, 'lavka': 110},
        'spb': {'__default__': 120},
    },
)
@pytest.mark.parametrize(
    'proc_update, expected_delay',
    [
        ({'$set': {'order.status': 'assigned'}}, None),
        ({'$set': {'performer.presetcar': False}}, None),
        ({'$unset': {'performer.seen': ''}}, None),
        ({'$unset': {'candidates.1.ost': ''}}, None),
        (None, 24),
        ({'$set': {'candidates.1.tariff_class': 'lavka'}}, 34),
        ({'$set': {'order.nz': 'spb'}}, 44),
        ({'$set': {'order.nz': 'spb', 'candidates.1.tags': ['deadman']}}, 74),
        (
            {'$set': {'candidates.1.tags': ['q', 'deadman', 'jack-sparrow']}},
            74,
        ),
        ({'$set': {'candidates.1.tags': ['bowie']}}, 24),
        ({'$set': {'candidates.1.gprs_time': 33.1}}, 57.1),
    ],
)
async def test_offer_timeout_eta(
        stq, stq_runner, mongodb, proc_update, expected_delay,
):
    order_id = 'order_1'
    args = [order_id, ['offertimeout']]

    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    if expected_delay is None:
        assert not stq.process_trigger.times_called
    else:
        next_call = stq.process_trigger.next_call()
        eta = _NOW + datetime.timedelta(seconds=expected_delay)
        assert next_call['eta'] == eta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'offertimeout' not in proc.get('trigger', {}).get('s', {})
