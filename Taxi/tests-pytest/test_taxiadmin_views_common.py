# -*- coding: utf-8 -*-
import collections
import pytest

from taxi.core import async
from taxi.internal import dbh
from taxiadmin.views import common


@pytest.inline_callbacks
def test_fill_card_cache(patch):
    class Card:
        def __init__(self, owner, card_id):
            self.owner = owner
            self.card_id = card_id
            self.persistent_id = 'persistent_id:' + card_id
            self.number = '1234****5678'

    calls_by_uid = collections.defaultdict(int)

    @patch('taxi.internal.card_operations.get_cards')
    @async.inline_callbacks
    def get_cards(owner_uid, cache_preferred, **kwargs):
        yield
        assert cache_preferred
        calls_by_uid[owner_uid] += 1
        if owner_uid == 'u1':
            async.return_value([Card('u1', 'x123'), Card('u1', 'x456'),
                                Card('u1', 'x789')])
        elif owner_uid == 'u2':
            async.return_value([Card('u2', 'x123'), Card('u2', 'x456'),
                                Card('u2', 'x012')])
        else:
            assert False, 'Unexpected owner uid!'

    order_docs = [
        {'billing_tech': {'transactions': [
            {'card_owner_uid': 'u1', 'card_payment_id': 'x123'},
            {'card_owner_uid': 'u2', 'card_payment_id': 'x456'},
        ]}},
        {'billing_tech': {'transactions': [
            {'card_owner_uid': 'u1', 'card_payment_id': 'x789'},
            {'card_owner_uid': 'u2', 'card_payment_id': 'x012'},
        ]}}
    ]

    cache = yield common.fill_card_cache(order_docs)
    assert cache == {
        ('x123', 'u1'): ('1234****5678', 'persistent_id:x123'),
        ('x456', 'u2'): ('1234****5678', 'persistent_id:x456'),
        ('x789', 'u1'): ('1234****5678', 'persistent_id:x789'),
        ('x012', 'u2'): ('1234****5678', 'persistent_id:x012'),
    }
    assert calls_by_uid == {'u1': 1, 'u2': 1}


@pytest.mark.parametrize('order_id,expected_indices', [
    (
        'some_py2_order_id',
        [(0, 2)]
    ),
    (
        'some_transactions_order_id',
        [(0, 1)]
    ),
])
@pytest.mark.filldb(
    orders='for_test_compensation_decision_pairs'
)
@pytest.inline_callbacks
def test_compensation_decision_pairs(order_id, expected_indices):
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    actual = common.compensation_decision_pairs(
        order_doc['billing_tech']['compensations'],
        list(order_doc['payment_tech']['history'])
    )
    assert actual == _make_pairs_from_indices_pairs(
        order_doc, expected_indices
    )


@pytest.mark.parametrize('chunk_size,expected_calls', [
    (1, [{'args': (['first_id'],)}, {'args': (['second_id'],)}]),
    (None, [{'args': (['first_id', 'second_id'],)}]),
    (2, [{'args': (['first_id', 'second_id'],)}]),
])
@pytest.inline_callbacks
def test_fetch_order_procs(patch, chunk_size, expected_calls):
    @patch('taxi.internal.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(
            ids, lookup_yt=True, src_tvm_service=None,
            skip_db=False, as_dbh=False, log_extra=None
    ):
        result = [
            {'_id': id_} for id_ in ids
        ]
        async.return_value(result)
        yield
    merged = yield common._fetch_order_procs(
        order_ids=['first_id', 'second_id'],
        chunk_size=chunk_size,
        skip_db=False,
        log_extra=None,
    )
    assert merged == [{'_id': 'first_id'}, {'_id': 'second_id'}]
    calls = [
        {'args': a_call['args']}
        for a_call in get_many_order_proc_by_ids.calls
    ]
    assert calls == expected_calls


def _make_pairs_from_indices_pairs(order_doc, indices):
    compensations = order_doc['billing_tech']['compensations']
    history = order_doc['payment_tech']['history']
    pairs = []
    for c, h in indices:
        pairs.append((compensations[c], history[h]))
    return pairs
