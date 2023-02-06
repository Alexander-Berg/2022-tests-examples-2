import datetime

import pytest

from taxi.core import db
from taxi.internal import user_antifraud_engine


@pytest.mark.parametrize('phone_doc,reason,multiorder', [
    ({'_id': '1234567890'}, 'test', False),
    ({'_id': '1234567890',
      'blocked_times': 5,
      'block_initiator': {
          'login': 'Tsar',
          'ticket': 'ASDFSAF',
      },
      'afs_block_reason': 'pushkin',
      'total': 700,
      'complete': 74,
      'bad_driver_cancels': 4,
      'blocked_till': datetime.datetime(2015, 11, 5),
      }, 'test_reason', False),
    ({'_id': '1234567890'}, 'test', True),
    ({'_id': '1234567890',
      'multiorder_blocked_times': 5,
      'block_initiator': {
          'login': 'Tsar',
          'ticket': 'ASDFSAF',
      },
      'multiorder_afs_block_reason': 'pushkin',
      'multioder_total': 700,
      'multiorder_complete': 74,
      'bad_driver_cancels': 4,
      'multiorder_blocked_till': datetime.datetime(2015, 11, 5),
      }, 'test_reason', True)
])
@pytest.mark.now('2015-10-30 10:30:00 +03:00')
@pytest.inline_callbacks
def test_rehabilitate_user(phone_doc, reason, multiorder):
    phone_id = yield db.antifraud_stat_phones.save(phone_doc)
    yield user_antifraud_engine.rehabilitate(
        phone_doc['_id'], reason=reason, is_multiorder=multiorder
    )

    doc = yield db.antifraud_stat_phones.find_one({'_id': phone_id})

    now = datetime.datetime.utcnow()
    assert doc['updated'] == now

    if not multiorder:
        assert doc['blocked_till'] == now
        assert doc['rehabilitated'] == now
        assert doc['rehabilitate_reason'] == reason

        assert 'blocked_times' not in doc
        assert 'block_initiator' not in doc
        assert 'afs_block_reason' not in doc
        assert 'bad_driver_cancels' not in doc
        assert 'total' not in doc
        assert 'complete' not in doc
    else:
        assert doc['multiorder_blocked_till'] == now
        assert doc['multiorder_rehabilitated'] == now
        assert doc['multiorder_rehabilitate_reason'] == reason

        assert 'multiorder_blocked_times' not in doc
        assert 'multiorder_afs_block_reason' not in doc
        assert 'multiorder_total' not in doc
        assert 'multiorder_complete' not in doc
