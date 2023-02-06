import typing

import bson
import pytest

from generated.models import user_api as user_api_models

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.email.allowed_unconfirmed import (
    allow_send_report_for_user,
)
from order_notify.repositories.email.user_email import get_user_email_doc
from order_notify.repositories.order_info import OrderData


EMAIL_DOCS: typing.List[dict] = [
    {
        'brand_name': 'yataxi',
        'confirmed': False,
        'id': '5dcec50b58204bb4a0e7e516',
        'personal_email_id': 'ad75d457e3804s11aee24220av6925de',
        'phone_id': '5fdcae29158d88efa226f134',
        'yandex_uid': '4034567950',
    },
    {
        'brand_name': 'yataxi',
        'confirmed': False,
        'id': '5fe0febd158d88dac3b1d66c',
        'phone_id': '5fe10671158d88dac3b1d67a',
        'yandex_uid': '4034567840',
    },
    {
        'brand_name': 'yataxi',
        'confirmed': True,
        'id': '5fe0febd158d88dac3b1d66c',
        'personal_email_id': 'd375d457e3804s11ael24220av6925de',
        'phone_id': '5fdcae29158d88efa226f134',
        'yandex_uid': '4034567840',
    },
    {
        'brand_name': 'yataxi',
        'confirmed': False,
        'id': '5fe0febd158d88dac3b1d66c',
        'personal_email_id': 'f745d457e3804s11ael24220avc9hfd5',
        'phone_id': 'a374cae29158d88efa227f1d',
        'yandex_uid': '4034567841',
    },
    {
        'brand_name': 'yataxi',
        'confirmed': True,
        'id': '5fe0febd158d88dac3b1d66c',
        'personal_email_id': 'f745d457e3804s11ael24220avc9hfd5',
        'phone_id': 'a374cae29158d88efa227f1d',
        'yandex_uid': '4034567841',
    },
    {
        'brand_name': 'yataxi',
        'confirmed': False,
        'id': '5fe0febd158d88dac3b1d66c',
        'phone_id': 'a374cae29158d88efa227f1d',
        'yandex_uid': '4034567841',
    },
]

EMAIL_OBJECT_NOT_COMPLETED = user_api_models.UserEmailObject(**EMAIL_DOCS[0])
EMAIL_OBJECT_WRONG = user_api_models.UserEmailObject(**EMAIL_DOCS[1])


CORRECT_ORDER_DATA = OrderData(
    brand='yataxi',
    country='rus',
    order={'nz': 'moscow'},
    order_proc={
        'order': {
            'application': 'android',
            'user_phone_id': bson.ObjectId('5fdcae29158d88efa226f134'),
            'user_uid': '4034567950',
        },
    },
)


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/user-api/users/get')
    async def users_handler(request):
        user_id = request.json['id']
        if user_id == '-1':
            return mockserver.make_response(
                json={'code': '404', 'message': 'Not found'}, status=404,
            )
        if user_id == '0':
            return {'id': '0'}
        if user_id == '1':
            return {
                'id': '1',
                'phone_id': 'phone_id_1',
                'yandex_uid': 'yandex_uid_1',
            }
        if user_id == '2':
            return {
                'id': '2',
                'phone_id': 'phone_id_2',
                'yandex_uid': 'yandex_uid_2',
                'yandex_uid_type': 'phonish',
            }
        if user_id == '3':
            return {
                'id': '3',
                'phone_id': 'phone_id_3',
                'yandex_uid': 'yandex_uid_3',
                'yandex_uid_type': 'web_cookie',
            }
        if user_id == '4':
            return {
                'id': '4',
                'phone_id': 'phone_id_4',
                'yandex_uid': 'yandex_uid_4',
                'yandex_uid_type': 'portal',
            }
        return {}

    @mockserver.json_handler('zalogin/v1/internal/phone-info')
    async def zalogin_phone_handler(request):
        if request.query['phone_id'] == 'phone_id_2':
            return {
                'items': [{'type': 'phonish', 'yandex_uid': 'yandex_uid_2b'}],
            }
        if request.query['phone_id'] == 'phone_id_3':
            return {
                'items': [{'type': 'phonish', 'yandex_uid': 'yandex_uid_3b'}],
            }
        return {'items': []}

    @mockserver.json_handler('/zalogin/v2/internal/uid-info')
    async def zalogin_uid_handler(request):
        if request.query['yandex_uid'] == 'yandex_uid_4':
            return {
                'yandex_uid': 'yandex_uid_4a',
                'type': 'portal',
                'bound_phonishes': [{'uid': 'yandex_uid_4b'}],
            }
        return {'items': []}

    return [users_handler, zalogin_phone_handler, zalogin_uid_handler]


@pytest.fixture(name='mock_functions')
def mock_user_emails_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_personal_email_doc = Counter()

    counters = Counters()

    @patch(
        'order_notify.repositories.email.user_email.'
        '_get_relevant_personal_email_doc',
    )
    async def _get_relevant_personal_email_doc(
            context: stq_context.Context,
            personal_email_ids: typing.Optional[typing.List[str]] = None,
            phone_ids: typing.Optional[typing.List[str]] = None,
            yandex_uids: typing.Optional[typing.List[str]] = None,
    ) -> typing.Optional[user_api_models.UserEmailObject]:
        counters.get_personal_email_doc.call()
        if personal_email_ids:
            return user_api_models.UserEmailObject(**EMAIL_DOCS[0])
        if phone_ids == ['phone_id_1'] and not yandex_uids:
            return user_api_models.UserEmailObject(**EMAIL_DOCS[1])
        if phone_ids == ['phone_id_2'] and yandex_uids == ['yandex_uid_2b']:
            return user_api_models.UserEmailObject(**EMAIL_DOCS[2])
        if phone_ids == ['phone_id_3'] and yandex_uids == ['yandex_uid_3b']:
            return user_api_models.UserEmailObject(**EMAIL_DOCS[3])
        if phone_ids is None and yandex_uids == [
                'yandex_uid_4',
                'yandex_uid_4b',
        ]:
            return user_api_models.UserEmailObject(**EMAIL_DOCS[4])
        return None


@pytest.mark.parametrize(
    'personal_email_id, user_id, expected_doc, expected_times_called',
    [
        pytest.param(
            'ad75d457e3804s11aee24220av6925de',
            '-2',
            EMAIL_DOCS[0],
            [0, 0, 0],
            id='personal_email_id',
        ),
        pytest.param(None, '-1', None, [1, 0, 0], id='no_user'),
        pytest.param(
            None, '0', None, [1, 0, 0], id='no_phone_id_and_yandex_uid',
        ),
        pytest.param(
            None, '1', EMAIL_DOCS[1], [1, 0, 0], id='no_uid_type_but_phone_id',
        ),
        pytest.param(
            None, '2', EMAIL_DOCS[2], [1, 1, 0], id='uid_type_phonish',
        ),
        pytest.param(
            None, '3', EMAIL_DOCS[3], [1, 1, 0], id='uid_type_web_cookie',
        ),
        pytest.param(
            None, '4', EMAIL_DOCS[4], [1, 0, 1], id='uid_type_portal',
        ),
    ],
)
async def test_get_user_email_doc(
        stq3_context: stq_context.Context,
        mock_server,
        mock_functions,
        personal_email_id,
        user_id,
        expected_doc,
        expected_times_called,
):
    email_doc = await get_user_email_doc(
        context=stq3_context,
        personal_email_id=personal_email_id,
        user_id=user_id,
    )
    times_called = [handler.times_called for handler in mock_server]
    assert times_called == expected_times_called
    if email_doc is None:
        assert expected_doc is None
    else:
        assert email_doc.serialize() == expected_doc


@pytest.mark.client_experiments3(
    consumer='order-notify/stq/send_ride_report_mail',
    config_name='send_ride_report_allow_unconfirmed',
    args=[
        {'name': 'zone', 'type': 'string', 'value': 'riga'},
        {
            'name': 'phone_id',
            'type': 'string',
            'value': '5fdcae29158d88efa226f134',
        },
        {'name': 'country', 'type': 'string', 'value': 'lva'},
    ],
    value={'enabled': True},
)
@pytest.mark.parametrize(
    'email_doc, order_data, expected_answer',
    [
        pytest.param(
            EMAIL_OBJECT_NOT_COMPLETED,
            CORRECT_ORDER_DATA,
            False,
            id='not_confirmed',
        ),
        pytest.param(
            user_api_models.UserEmailObject(**EMAIL_DOCS[2]),
            CORRECT_ORDER_DATA,
            True,
            id='confirmed',
        ),
        pytest.param(
            EMAIL_OBJECT_NOT_COMPLETED,
            OrderData(
                brand='uber',
                country='lva',
                order={'nz': 'riga'},
                order_proc={
                    'order': {'user_phone_id': '5fdcae29158d88efa226f134'},
                },
            ),
            True,
            id='not_confirmed_but_latvia',
        ),
    ],
)
async def test_allow_send_report_for_user(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        email_doc,
        order_data,
        expected_answer,
):
    answer = await allow_send_report_for_user(
        context=stq3_context, email_doc=email_doc, order_data=order_data,
    )
    assert answer == expected_answer
