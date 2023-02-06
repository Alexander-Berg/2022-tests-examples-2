import pytest

from taxi.internal import archive
from taxi.internal import dbh
from taxi.taxi_protocol.protocol_1x import client as taxi_client


@pytest.mark.parametrize(
    'order_id,was_sent',
    [
        ('no1', False),
        ('no1', True),
        ('no2', False),
        ('no2', True),
    ]
)
@pytest.inline_callbacks
def test_update_notification(order_id, was_sent):
    notif = 'payment'
    order_doc = yield dbh.orders.Doc.find_one_by_exact_id(order_id)
    if order_doc['_id'] == 'no3':
        order_doc['payment_tech']['notifications'][notif]['to_send'] = 123

    yield taxi_client._update_notification(order_doc, notif, was_sent)

    modified_doc = yield dbh.orders.Doc.find_one_by_exact_id(order_id)
    modified_part = modified_doc['payment_tech']['notifications'][notif]

    if was_sent:
        assert modified_part['to_send'] == modified_part['sent']
    else:
        if modified_part['to_send'] is None:
            assert modified_part['attempts'] == 0
        else:
            assert modified_part['attempts'] == 1

    if order_doc['_id'] == 'no2' and was_sent:
        assert modified_part['sent'] is not None

    if order_doc['_id'] == 'no3':
        assert modified_part['sent'] is None
        assert modified_part['to_send'] is None


@pytest.mark.parametrize(
    'order_id,expected_can_be_ignored,expected_error',
    [
        ('performer_with_cost', False, None),
        ('no_performer_without_cost', True, None),
        ('no_performer_with_cost', None, 'SendPaymentPerformerError'),
    ]
)
@pytest.inline_callbacks
def test_can_be_ignored(order_id, expected_can_be_ignored, expected_error):

    order_proc = yield archive.get_order_proc_by_id(
        order_id, secondary=False
    )
    order_proc = dbh.order_proc.Doc(order_proc)

    if expected_error:
        with pytest.raises(taxi_client.SendPaymentPerformerError):
            yield taxi_client._can_be_ignored(order_proc)
    else:
        can_be_ignored = yield taxi_client._can_be_ignored(order_proc)
        assert can_be_ignored == expected_can_be_ignored
