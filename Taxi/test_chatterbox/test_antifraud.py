import pytest

from chatterbox.internal import antifraud


@pytest.mark.parametrize(
    'task,solution',
    [
        ({'chat_type': 'client', 'meta_info': {}}, True),
        ({'chat_type': 'sms', 'meta_info': {'order_id': 'order_id'}}, True),
        (
            {'chat_type': 'startrack', 'meta_info': {'order_id': 'order_id'}},
            True,
        ),
        (
            {
                'chat_type': 'driver',
                'meta_info': {
                    'order_id': 'order_id',
                    'driver_license_personal_id': 'driver_license_personal_id',
                },
            },
            True,
        ),
        ({'chat_type': 'driver', 'meta_info': {}}, True),
        ({'chat_type': 'client_eats', 'meta_info': {}}, True),
        ({'chat_type': 'lavka', 'meta_info': {}}, True),
        ({'chat_type': 'market', 'meta_info': {}}, True),
        ({'chat_type': 'sms', 'meta_info': {}}, False),
        ({'chat_type': 'startrack', 'meta_info': {}}, False),
    ],
)
@pytest.mark.config(
    SERVICES_FOR_REQUESTS_TO_ANTIFRAUD=[
        'client',
        'driver',
        'client_eats',
        'lavka',
        'market',
    ],
)
async def test_antifraud(task, solution, cbox_app):
    assert antifraud.check_request_antifraud(task, cbox_app.config) == solution
