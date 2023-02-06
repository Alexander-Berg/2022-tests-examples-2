from __future__ import unicode_literals

import datetime

import pytest

from taxi.core import db
from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2017-08-20T15:00:00.0')
@pytest.inline_callbacks
def test_create(patch):
    yield db.childchair_rent.remove()
    yield db.childchair_rent_transactions.remove()
    doc_template = dict(
        order_id='order_id',
        alias_id='alias_id',
        clid='clid',
        db_id='db_id',
        uuid='uuid',
        due=datetime.datetime(2017, 8, 20, 10, 10),
        order_created=datetime.datetime(2017, 8, 20, 10),
        currency='RUB',
        nearest_zone='moscow',
        contract_id='child_chair_contract',
        base_doc_id=3141592654,
        payment_type='cash',
        order_completed_at=datetime.datetime(2017, 8, 20, 10, 10),
        prefer_payout_flow=False,
    )
    entry = dbh.childchair_rent_transactions.Doc.make_bulk_entry(
        value=200, without_vat='180', **doc_template
    )
    yield dbh.childchair_rent_transactions.Doc.add_many_records([entry])
    tr = yield db.childchair_rent_transactions.find({}, {'_id': 0}).sort('version').run()
    trans = [dict(
        prev_rent=None,
        prev_without_vat=None,
        cur_rent=200,
        cur_without_vat='180',
        version=1,
        created=datetime.datetime(2017, 8, 20, 15),
        **doc_template
    )]
    assert tr == trans

    entry = yield dbh.childchair_rent_transactions.Doc.make_bulk_entry(
        value=200, without_vat='180', **doc_template
    )
    yield dbh.childchair_rent_transactions.Doc.add_many_records([entry])
    tr = yield db.childchair_rent_transactions.find({}, {'_id': 0}).sort('version').run()
    assert tr == trans

    entry = dbh.childchair_rent_transactions.Doc.make_bulk_entry(
        value=150, without_vat='130', **doc_template
    )
    yield dbh.childchair_rent_transactions.Doc.add_many_records([entry])
    tr = yield db.childchair_rent_transactions.find({}, {'_id': 0}).sort('version').run()
    trans.append(dict(
        prev_rent=200,
        prev_without_vat='180',
        cur_rent=150,
        cur_without_vat='130',
        version=2,
        created=datetime.datetime(2017, 8, 20, 15),
        **doc_template
    ))
    assert tr == trans
