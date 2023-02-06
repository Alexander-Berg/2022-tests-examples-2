import bson
import pytest

from order_notify.country_features.latvia_invoice_attachment import (
    is_white_car_number,
)
from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData


PHONE_ID = '5fdcae29158d88efa226f134'


@pytest.mark.client_experiments3(
    consumer='order-notify/stq/'
    'send_ride_report_mail_latvia_invoice_attachment',
    experiment_name='latvia_extra_invoice_attachment',
    args=[
        {'name': 'zone', 'type': 'string', 'value': 'riga'},
        {'name': 'phone_id', 'type': 'string', 'value': PHONE_ID},
        {'name': 'country', 'type': 'string', 'value': 'lva'},
    ],
    value={'excluded_plates': ['TQ', 'TX', 'EX', 'TE']},
)
@pytest.mark.parametrize(
    'order_data, expected_answer',
    [
        pytest.param(
            OrderData(
                brand='',
                country='',
                order={},
                order_proc={'order': {'performer': {}}},
            ),
            False,
            id='empty car number',
        ),
        pytest.param(
            OrderData(
                brand='yango',
                country='lva',
                order={'nz': 'moscow'},
                order_proc={
                    'order': {
                        'user_phone_id': bson.ObjectId(PHONE_ID),
                        'performer': {'car_number': 'AA1234'},
                    },
                },
            ),
            False,
            id='white number but not latvia',
        ),
        pytest.param(
            OrderData(
                brand='yango',
                country='lva',
                order={'nz': 'riga'},
                order_proc={
                    'order': {
                        'user_phone_id': bson.ObjectId(PHONE_ID),
                        'performer': {'car_number': 'AA1234'},
                    },
                },
            ),
            True,
            id='white number',
        ),
        pytest.param(
            OrderData(
                brand='yango',
                country='lva',
                order={'nz': 'riga'},
                order_proc={
                    'order': {
                        'user_phone_id': bson.ObjectId(PHONE_ID),
                        'performer': {'car_number': 'TQ1234'},
                    },
                },
            ),
            False,
            id='not white number',
        ),
    ],
)
async def test_is_white_number(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        order_data,
        expected_answer,
):
    answer = await is_white_car_number(
        context=stq3_context, order_data=order_data,
    )
    assert answer == expected_answer
