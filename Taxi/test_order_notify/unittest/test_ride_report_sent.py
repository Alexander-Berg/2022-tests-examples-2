import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import ride_report_sent


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'order_id, set_value',
    [
        pytest.param('some_true_order', False, id='set_not_sent'),
        pytest.param('some_false_order', True, id='set_sent'),
    ],
)
async def test_update_ride_report_sent_value(
        stq3_context: stq_context.Context, mongo, order_id, set_value,
):
    value_in_base = not set_value

    mongo_docs_count = await mongo.order_reports_sent.count(
        {'ride_report_sent': value_in_base},
    )
    assert mongo_docs_count == 2

    await ride_report_sent.update_ride_report_sent_value(
        context=stq3_context, order_id=order_id, value=set_value,
    )

    mongo_docs_not_change_count = await mongo.order_reports_sent.count(
        {'ride_report_sent': value_in_base},
    )
    assert mongo_docs_not_change_count == 1
    mongo_docs_change_count = await mongo.order_reports_sent.count(
        {'_id': order_id, 'ride_report_sent': set_value},
    )
    assert mongo_docs_change_count == 1
