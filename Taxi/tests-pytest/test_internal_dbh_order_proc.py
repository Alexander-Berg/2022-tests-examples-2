import datetime

import bson
import bson.json_util
import pytest

from taxi.core import arequests
from taxi.core import async
from taxi.core.db import classes as db_classes
from taxi.external import archive as external_archive
from taxi.internal import archive
from taxi.internal import dbh
from taxi.internal import order_core

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_modify_update_with_autoreorder(monkeypatch, mock_send_event):
    # Test that `_modify_update_with_autoreorder()` works without
    # exceptions

    update_ = {}
    event = {}
    reason = 'my_reason'
    dbh.order_proc.Doc._modify_update_with_autoreorder(update_, event, reason)

    def mock_find_and_modify(self, query, update, *args, **kwargs):
        # Shortcut
        sucls = dbh.order_proc.Doc.order_info.statistics.status_updates

        assert update['$push'][sucls][sucls.reason.key] == reason
        return {'_id': 'order_id'}

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )

    yield order_core.send_event(
        'order_id', event=event, update=update_, tag='admin')


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('candidate_vgw_phone', [
    None,
    {'candidates.2.forwarding':
        {
            'phone': '+749500000000',
            'ext': '007'
        }
    },
])
@pytest.mark.parametrize('check_card_is_finished', [
    None,
    {'payment_tech.check_card_is_finished': True},
])
@pytest.mark.config(PY2_PROCESSING_UPDATE_PROC_IN_PROCAAS=True)
@pytest.inline_callbacks
def test_mark_as_sync_and_update_proc_in_procaas(candidate_vgw_phone, check_card_is_finished):
    class Proc(dbh.order_proc.Doc):
        calls = []

        @classmethod
        @async.inline_callbacks
        def _find_and_commit_processing(
                cls, order_id, query=None, update=None,
                processing_version=None):
            yield
            cls.calls.append((query, update))
            async.return_value()

    proc = Proc()
    proc._commit_by_procaas = True
    if candidate_vgw_phone is not None:
        proc.preupdated_proc_data.candidate_vgw_phone = candidate_vgw_phone
    if check_card_is_finished is not None:
        proc.preupdated_proc_data.check_card_is_finished = check_card_is_finished

    (update, query) = yield proc.mark_as_sync(event_index=0)

    expected_update = {'$set': {}}
    if candidate_vgw_phone:
        expected_update['$set'].update(candidate_vgw_phone)
    if check_card_is_finished:
        expected_update['$set'].update(check_card_is_finished)
    if not expected_update['$set']:
        expected_update = None

    assert (query, update) == (None, expected_update)


@pytest.mark.parametrize('granted_promotions', [
    None,
    [],
    ['tesla', 'shmesla'],
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_mark_as_sync_and_granted_promotions(granted_promotions):
    class Proc(dbh.order_proc.Doc):
        calls = []

        @classmethod
        @async.inline_callbacks
        def _find_and_commit_processing(
                cls, order_id, query=None, update=None,
                processing_version=None):
            yield
            cls.calls.append((query, update))
            async.return_value()

    proc = Proc()
    if granted_promotions is not None:
        proc.preupdated_order_data.granted_promotions = granted_promotions

    (update, query) = yield proc.mark_as_sync(event_index=0)

    expected_update = None
    if granted_promotions:
        expected_update = {
            '$set': {Proc.order.granted_promotions: granted_promotions},
        }
    elif granted_promotions is not None:
        expected_update = {'$unset': {Proc.order.granted_promotions: True}}

    assert (query, update) == (None, expected_update)


@pytest.mark.filldb(_fill=False)
def test_get_last_change():
    class Stub:
        name = 'name'
        another_name = 'another_name'

    lco = dbh.order_proc.Doc.changes.objects
    proc = dbh.order_proc.Doc({
        dbh.order_proc.Doc.changes: {
            lco.key: [
                {
                    lco.name.key: Stub.name,
                    lco.value.key: 1,
                },
                {
                    lco.name.key: Stub.another_name,
                    lco.value.key: 2,
                },
                {
                    lco.name.key: Stub.name,
                    lco.value.key: 3,
                },
            ],
        },
    })

    assert proc.get_last_change(Stub.name).value == 3
    assert proc.get_last_change(Stub.another_name).value == 2
    assert proc.get_last_change('not_existen_name') is None


@pytest.mark.parametrize('order_id,name,expected_name_statuses', [
    ('cant_skip_the_only_one_id', 'comment', [{'comment': 'init'}]),
    ('cant_skip_last_applied_id', 'comment',
     [{'comment': 'init'}, {'comment': {}}]),
    ('dont_touch_other_names_id', 'comment',
     [{'comment': 'skipped'}, {'porchnumber': 'init'}, {'comment': 'done'}]),
    ('cant_skipped_done_id', 'comment',
     [{'comment': 'done'}, {'comment': 'done'}]),
    ('cant_skipped_failed_id', 'comment',
     [{'comment': 'failed'}, {'comment': 'done'}]),
    ('cant_skipped_skipped_id', 'comment',
     [{'comment': 'skipped'}, {'comment': 'done'}]),
    ('skipped_if_more_recent_failed', 'comment',
     [{'comment': 'skipped'}, {'comment': 'failed'}]),
    ('skipped_if_more_recent_init', 'comment',
     [{'comment': 'skipped'}, {'comment': 'init'}]),
    ('skipped_if_more_recent_processing', 'comment',
     [{'comment': 'skipped'}, {'comment': 'processing'}]),
    ('skipped_multiple', 'comment',
     [{'comment': 'skipped'}, {'comment': 'skipped'},
      {'comment': 'processing'}]),
    ('no_performer', 'comment',
     [{'comment': 'skipped'}, {'comment': 'skipped'}]),
])
@pytest.mark.filldb(
    order_proc='for_mark_skipped_test'
)
@pytest.inline_callbacks
def test_mark_send_skipped_applied_changes(
        order_id, name, expected_name_statuses):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc = yield proc.mark_send_skipped_applied_changes(name)
    name_statuses = [
        {obj.name: obj.send_status.status} for obj in proc.changes.objects
    ]
    assert name_statuses == expected_name_statuses


@pytest.mark.filldb(
    order_proc='for_mark_skipped_test'
)
@pytest.inline_callbacks
def test_mark_send_skipped_applied_changes_failure(patch):
    now_find_and_modify_always_returns_none(patch)

    order_id = 'skipped_if_more_recent_init'
    name = 'comment'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    with pytest.raises(dbh.order_proc.RaceCondition):
        yield proc.mark_send_skipped_applied_changes(name)


@pytest.mark.filldb(
    order_proc='for_mark_skipped_test'
)
@pytest.mark.parametrize('kwargs,expected_query', [
    (
        {
            'order_id': 'some_order_id',
        },
        {
            '_shard_id': 0,
            dbh.order_proc.Doc._id: 'some_order_id',
            dbh.order_proc.Doc.order.taxi_status: {
                '$in': dbh.order_proc._AUTOREORDER_DRIVING_TAXI_STATUSES
            },
            dbh.order_proc.Doc.status: dbh.order_proc.STATUS_ASSIGNED,
        },
    ),
])
@pytest.inline_callbacks
def test_do_autoreorder_query(
        kwargs, expected_query, monkeypatch, mock_send_event,
):
    # Test how `do_autoreorder()` forms query

    queries = []

    def mock_find_and_modify(self, query, *args, **kwargs):
        queries.append(query)
        return {
            '_id': query['_id'],
        }

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )

    yield dbh.order_proc.Doc.do_autoreorder(**kwargs)
    assert queries == [expected_query]


@pytest.mark.parametrize('order_id,expected_name_statuses', [
    ('it_skips_all_except_the_last_one_id',
     [{'comment': 'skipped'}, {'comment': 'skipped'}, {'comment': 'pending'}]),
    ('its_okay_with_no_changes_id', []),
    ('its_okay_with_empty_changes_id', []),
    ('it_ignores_not_active_id',
     [{'comment': 'applying'}, {'comment': 'applying'}]),
    ('it_doesnt_skip_the_only_one_id', [{'comment': 'pending'}]),
    ('it_doesnt_skip_the_last_one_id',
     [{'comment': 'skipped'}, {'comment': 'pending'}]),
    ('it_ignores_other_names_id',
     [{'porchnumber': 'pending'}, {'comment': 'pending'}]),
])
@pytest.mark.filldb(
    order_proc='for_mark_skipped_active_changes_test'
)
@pytest.inline_callbacks
def test_mark_skipped_active_changes(order_id, expected_name_statuses):
    name = 'comment'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc = yield proc.mark_skipped_active_changes(name)
    name_statuses = [
        {obj.name: obj.status} for obj in proc.changes.objects
    ]
    assert name_statuses == expected_name_statuses


@pytest.mark.filldb(
    order_proc='for_mark_skipped_active_changes_test'
)
@pytest.inline_callbacks
def test_mark_skipped_active_changes_failure(patch):
    now_find_and_modify_always_returns_none(patch)

    order_id = 'it_skips_all_except_the_last_one_id'
    name = 'comment'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    with pytest.raises(dbh.order_proc.RaceCondition):
        yield proc.mark_skipped_active_changes(name)


def now_find_and_modify_always_returns_none(patch):
    @patch('taxi.internal.dbh.order_proc.Doc._find_and_modify')
    def _find_and_modify(*args, **kwargs):
        return None


@pytest.mark.filldb(
    order_proc='for_update_active_change_status_test'
)
@pytest.mark.parametrize('order_id,status,expected_name_statuses', [
    ('it_updates_active_change_status_id', 'applying',
     [{'comment': 'pending'}, {'comment': 'applying'}]),
])
@pytest.inline_callbacks
def test_update_active_change_status(
        order_id, status, expected_name_statuses, patch):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    name = 'comment'
    yield proc.update_active_change_status(name, status)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    name_statuses = [
        {obj.name: obj.status} for obj in proc.changes.objects
    ]
    assert name_statuses == expected_name_statuses


@pytest.mark.filldb(
    order_proc='for_update_active_change_status_test'
)
@pytest.mark.parametrize('order_id,status', [
    ('it_updates_active_change_status_id', 'applying'),
])
@pytest.inline_callbacks
def test_update_active_change_status_failure(monkeypatch, order_id, status):
    def mock_find_and_modify(*args, **kwargs):
        pass

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    name = 'comment'
    with pytest.raises(dbh.order_proc.RaceCondition):
        yield proc.update_active_change_status(name, status)


@pytest.mark.filldb(_fill=False)
def test_get_prev_status_updates():
    # Check:
    # 1. order of returned objects
    # 2. returned objects (must be Humbledb objects, not just dicts)
    proc_cls = dbh.order_proc.Doc
    status_updates_cls = proc_cls.order_info.statistics.status_updates
    proc = proc_cls({
        proc_cls.order_info.key: {
            proc_cls.order_info.statistics.key: {
                status_updates_cls.key: [
                    {status_updates_cls.reason.key: 'one'},
                    {status_updates_cls.reason.key: 'two'},
                    {status_updates_cls.reason.key: 'three'},
                    {status_updates_cls.reason.key: 'four'},
                ],
            },
        },
    })
    result = [x.reason for x in proc.get_prev_status_updates(2)]
    assert result == ['two', 'one']
    assert list(proc.get_prev_status_updates(0)) == []

    # It works correctly with an empty object
    assert list(proc_cls().get_prev_status_updates(0)) == []


@pytest.mark.filldb(order_proc='assigned')
@pytest.inline_callbacks
def test_can_cancel_in_assigned(mock_send_event):
    yield dbh.order_proc.Doc.update_taxi_status(
        order_id='1',
        taxi_status=dbh.orders.TAXI_STATUS_CANCELLED,
        reason='some_reason',
        event_key='admin-cancel',
        idempotency_token='admin-cancel-as-park',
        tag='admin',
    )
    doc = yield dbh.order_proc.Doc.find_one_by_id('1')
    assert doc.order.taxi_status == dbh.orders.TAXI_STATUS_CANCELLED
    assert doc.order.status == dbh.orders.STATUS_FINISHED


@pytest.mark.filldb(order_proc='assigned')
@pytest.inline_callbacks
def test_autoreorder_in_assignred(mock_send_event):
    yield dbh.order_proc.Doc.do_autoreorder(order_id='1', any_status=False)
    doc = yield dbh.order_proc.Doc.find_one_by_id('1')
    assert doc.order.taxi_status == dbh.orders.TAXI_STATUS_NONE
    assert doc.order.status == dbh.orders.STATUS_PENDING


@pytest.mark.filldb(order_proc='find')
@pytest.inline_callbacks
def test_archive(patch, load):
    @patch('taxi.external.archive._perform_post_order_archive')
    @async.inline_callbacks
    def _perform_post(location, payload, src_tvm_service=None, log_extra=None):
        order_proc = bson.json_util.loads(load(
            'yt_archive_order_proc_find.json'
        ))
        order_found = False
        if order_proc['_id'] == payload['id']:
            order_found = True
        if (
                'indexes' in payload and 'reorder' in payload['indexes'] and
                order_proc['reorder']['id'] == payload['id']
        ):
            order_found = True
        if (
                'indexes' in payload and 'alias' in payload['indexes'] and
                order_proc['aliases'][0]['id'] == payload['id']
        ):
            order_found = True
        if not order_found:
            raise external_archive.NotFoundError

        response_json = {'doc': order_proc}
        response = bson.BSON.encode(response_json)
        yield async.return_value(arequests.Response(
            status_code=200, content=response
        ))

    cls = dbh.order_proc.Doc

    def find_one_mine(order_id):
        return cls.find_one_mine(order_id, 'phone_id')

    params = [
        (archive.get_order_proc_by_id, 'id', True),
        (archive.get_order_proc_by_id, 'reorder_id', True),
        (archive.get_order_proc_by_id, 'alias_id', False),
        (archive.get_order_proc_by_id, 'archive_id', True),
        (archive.get_order_proc_by_id, 'archive_reorder_id', True),
        (archive.get_order_proc_by_id, 'archive_alias_id', False),

        (archive.get_order_proc_by_exact_alias, 'id', False),
        (archive.get_order_proc_by_exact_alias, 'reorder_id', False),
        (archive.get_order_proc_by_exact_alias, 'alias_id', True),
        (archive.get_order_proc_by_exact_alias, 'archive_id', True),
        (archive.get_order_proc_by_exact_alias, 'archive_reorder_id', False),
        (archive.get_order_proc_by_exact_alias, 'archive_alias_id', True),

        (archive.get_order_proc_by_id_or_alias, 'id', True),
        (archive.get_order_proc_by_id_or_alias, 'reorder_id', True),
        (archive.get_order_proc_by_id_or_alias, 'alias_id', True),
        (archive.get_order_proc_by_id_or_alias, 'archive_id', True),
        (archive.get_order_proc_by_id_or_alias, 'archive_reorder_id', True),
        (archive.get_order_proc_by_id_or_alias, 'archive_alias_id', True),

        (find_one_mine, 'id', True),
        (find_one_mine, 'reorder_id', True),
        (find_one_mine, 'alias_id', False),
        (find_one_mine, 'archive_id', False),
        (find_one_mine, 'archive_reorder_id', False),
        (find_one_mine, 'archive_alias_id', False),
    ]

    for method, id, success in params:
        print method, id
        if success:
            proc = yield method(id)
            assert proc['_id'].startswith('archive') == id.startswith('archive')
        else:
            if method == find_one_mine:
                with pytest.raises(dbh.order_proc.NotFound):
                    yield method(id)
            else:
                with pytest.raises(archive.NotFound):
                    yield method(id)


@pytest.mark.filldb(order_proc='moved_to_cash')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'phone_id,order_id,exception,with_coupon',
    [
        ('phone_id', 'order_id', None, False,),
        ('phone_id', 'wrong_order_id', dbh.order_proc.NotFound, False),
        ('phone_id', 'order_id', None, True),
        ('phone_id', 'wrong_order_id', dbh.order_proc.NotFound, True),
    ]
)
@pytest.mark.parametrize('force_action', [(True), (False)])
@pytest.inline_callbacks
def test_enqueue_on_moved_to_cash(phone_id, order_id, exception, with_coupon,
                                  force_action, mock_send_event):
    if exception is not None:
        with pytest.raises(dbh.order_proc.NotFound):
            yield dbh.order_proc.Doc.enqueue_on_moved_to_cash(
                order_id, phone_id, reason_code='test', with_coupon=with_coupon,
                force_action=force_action,
            )
    else:
        yield dbh.order_proc.Doc.enqueue_on_moved_to_cash(
            order_id, phone_id, reason_code='test', with_coupon=with_coupon,
            force_action=force_action,
        )
        proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)
        assert len(proc.order_info.statistics.status_updates) == 1
        event = proc.order_info.statistics.status_updates[0]
        assert event.pop('x-idempotency-token', None) is not None
        assert event == {
            'q': 'moved_to_cash',
            'c': NOW,
            'h': True,
            'a': {
                'reason_code': 'test',
                'with_coupon': with_coupon,
                'invalidate_transactions': False,
                'force_action': force_action,
            }
        }


@pytest.mark.filldb(order_proc='debt_allowed')
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_notify_on_debt_allowed(mock_send_event):
    phone_id = 'phone_id'
    order_id = 'order_id'
    yield dbh.order_proc.Doc.notify_on_debt_allowed(
        order_id, phone_id, 'test_reason')
    proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)

    assert len(proc.order_info.statistics.status_updates) == 1
    event = proc.order_info.statistics.status_updates[0]
    assert event.pop('x-idempotency-token', None) is not None
    assert event == {
        'q': 'debt_allowed',
        'c': NOW,
        'h': True,
        'a': {
            'reason_code': 'test_reason',
        },
    }


@pytest.mark.filldb(
    order_proc='for_test_get_statistics'
)
@pytest.mark.parametrize('proc_id,expected_statistics', [
    (
        'some_cancelled_order_id',
        dbh.order_proc.Statistics(
            cancel_time=181.0,
            cancel_distance=155725.65744551463,
            travel_time=None,
            travel_distance=None,
            total_time=None,
            total_distance=None,
            complete_time=None,
            start_waiting_time=None,
            start_transporting_time=None,
        )
    ),
    (
        'some_complete_order_id',
        dbh.order_proc.Statistics(
            cancel_time=None,
            cancel_distance=None,
            travel_time=603.0,
            travel_distance=6666,
            total_time=None,
            total_distance=None,
            complete_time=datetime.datetime(2017, 8, 3, 17, 8, 3),
            start_waiting_time=None,
            start_transporting_time=datetime.datetime(2017, 8, 3, 16, 58),
        )
    )
])
@pytest.inline_callbacks
def test_get_statistics(proc_id, expected_statistics):
    proc = yield dbh.order_proc.Doc.find_one_by_id(proc_id)
    assert proc.get_statistics() == expected_statistics


_NOW = datetime.datetime(2017, 11, 1, 13, 43, 55)
_MOVE_UPDATE = {
    'c': _NOW,
    'q': 'related_moved_to_cash',
    'a': {
        'decision_id': 'some-decision-id',
        'source_order_id': 'source-order',
    },
    'x-idempotency-token': 'related-switch-to-cash:some-decision-id',
    'h': True,
}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'status_updates, decision_id, expected_updates, exception', [
        ([], 'some-decision-id', [_MOVE_UPDATE], None),
        (
            [{'c': _NOW, 's': 'transporting', 'q': 'started'}],
            'some-decision-id',
            [{'c': _NOW, 's': 'transporting', 'q': 'started'}, _MOVE_UPDATE],
            None,
        ),
        (
            [_MOVE_UPDATE], 'some-decision-id', [_MOVE_UPDATE],
            dbh.order_proc.RaceCondition,
        ),
        (
            [_MOVE_UPDATE, {'c': _NOW, 's': 'transporting', 'q': 'started'}],
            'some-decision-id',
            [_MOVE_UPDATE, {'c': _NOW, 's': 'transporting', 'q': 'started'}],
            dbh.order_proc.RaceCondition,
        ),
        (
            [_MOVE_UPDATE],
            'other-decision-id',
            [_MOVE_UPDATE, {
                'c': _NOW,
                'q': 'related_moved_to_cash',
                'a': {
                    'decision_id': 'other-decision-id',
                    'source_order_id': 'source-order',
                },
                'x-idempotency-token': 'related-switch-to-cash:other-decision-id',
                'h': True,
            }],
            None
        )
    ]
)
@pytest.mark.filldb()
@pytest.inline_callbacks
def test_related_switch_to_cash(
        status_updates, decision_id, expected_updates, exception,
        mock_send_event,
):
    update = {
        'order_info': {
            'statistics': {
                'status_updates': status_updates
            }
        },
        '_shard_id': 0,
    }
    proc = yield dbh.order_proc.Doc.update_and_return(
        {'_id': 'proc'}, update, upsert=True)
    assert proc is not None
    if exception is not None:
        with pytest.raises(exception):
            yield dbh.order_proc.Doc.send_related_switch_to_cash(
                'proc', decision_id, 'source-order'
            )
    else:
        yield dbh.order_proc.Doc.send_related_switch_to_cash(
            'proc', decision_id, 'source-order'
        )

    proc = yield dbh.order_proc.Doc.find_one_by_id('proc')
    actual_updates = proc.order_info.statistics.status_updates
    assert actual_updates == expected_updates


@pytest.mark.filldb
@pytest.mark.parametrize(
    'modifier_pay_subventions,pay_subventions,tariffs,'
    'tariff_class,expected_value',
    [
        (None, None, ['econom'], 'econom', 0.9),
        (True, None, ['econom'], 'econom', 0.9),
        (False, None, ['econom'], 'econom', 0.9),
        (True, False, ['econom'], 'econom', None),
        (False, False, ['econom'], 'econom', 0.9),
        (True, True, ['econom'], 'econom', 0.9),
        (False, True, ['econom'], 'econom', None),
        (True, True, ['comform'], 'econom', None),
        (False, False, ['comform'], 'econom', None),
    ]
)
@pytest.inline_callbacks
def test_get_price_multiplier(
        modifier_pay_subventions, pay_subventions, tariffs,
        tariff_class, expected_value
):
    proc = yield dbh.order_proc.Doc.find_one_by_id('id')
    proc.price_modifiers['items'][0]['pay_subventions'] = modifier_pay_subventions
    proc.price_modifiers['items'][0]['tariff_categories'] = tariffs
    assert proc.get_discount_multiplier(
        tariff_class=tariff_class,
        pay_subventions=pay_subventions
    ) == expected_value


@pytest.mark.parametrize(
    'order_id,expected_time_range',
    [
        (
            'order_1',
            (datetime.datetime(2018, 6, 17), datetime.datetime(2018, 6, 18)),
        ),
        (
            'order_2',
            (datetime.datetime(2018, 6, 16), datetime.datetime(2018, 6, 19)),
        ),
        ('order_3', None),
        ('order_4', None),
    ]
)
@pytest.mark.filldb(order_proc='test_get_status_update_time_range')
@pytest.inline_callbacks
def test_get_status_update_time_range(order_id, expected_time_range):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    time_range = proc.get_status_update_time_range()
    assert time_range == expected_time_range


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_notify_on_moneyflow(monkeypatch, mock_send_event):
    result = {}

    def mock_find_and_modify(self, query, update, *args, **kwargs):
        result['query'] = query
        result['update'] = update
        return {'_id': 'order-id'}

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )

    yield dbh.order_proc.Doc.notify_on_moneyflow(
        'order-id', 500, 'idempotency-key', log_extra=None)
    assert result['query'] == {'_id': 'order-id', '_shard_id': 0}
    assert result['update'] == {
        '$set': {
            'processing.need_start': True,
        },
        '$currentDate': {'updated': True},
        '$inc': {'processing.version': 1, 'order.version': 1},
        '$push': {'order_info.statistics.status_updates': {
            'q': 'moneyflow',
            'h': True,
            'c': datetime.datetime.utcnow(),
            'a': {'paid_amount': 500},
            'x-idempotency-token': 'idempotency-key',
        }}
    }


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_notify_on_debt_allowed_2(monkeypatch, mock_send_event):
    result = {}

    def mock_find_and_modify(self, query, update, *args, **kwargs):
        result['query'] = query
        result['update'] = update
        return {'_id': 'order-id'}

    monkeypatch.setattr(
        db_classes.BaseCollectionWrapper, 'find_and_modify', mock_find_and_modify
    )

    yield dbh.order_proc.Doc.notify_on_debt_allowed(
        'order-id', 'phone-id', 'DEBT_ALLOWED')
    assert result['query'] == {
        '_id': 'order-id',
        '_shard_id': 0,
    }
    su = result['update']['$push']['order_info.statistics.status_updates']
    assert su.pop('x-idempotency-token') is not None
    assert result['update'] == {
        '$set': {
            'processing.need_start': True,
        },
        '$currentDate': {'updated': True},
        '$inc': {'processing.version': 1, 'order.version': 1},
        '$push': {'order_info.statistics.status_updates': {
            'q': 'debt_allowed',
            'h': True,
            'c': datetime.datetime.utcnow(),
            'a': {'reason_code': 'DEBT_ALLOWED'}
        }}
    }
