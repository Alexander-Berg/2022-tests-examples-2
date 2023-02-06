import typing

import pytest

from generated.models import corp_clients as corp_clients_models
from generated.models import user_api as user_api_models

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import send_report_functions
from order_notify.repositories.email.message import Message
from order_notify.repositories.order_info import OrderData


NONE_EMAIL_DOC_PERSONAL_EMAIL_ID = 'none_email_doc'
NONE_PERSONAL_EMAIL_ID = 'none_personal_email_id'
NOT_CONFIRMED_PERSONAL_EMAIL_ID = 'not_confirmed_not_send'
NOT_CONFIRMED_BUT_SEND_PERSONAL_EMAIL_ID = 'not_confirmed_but_send'
CONFIRMED_PERSONAL_EMAIL_ID = 'confirmed_send'


@pytest.fixture(name='mock_functions')
def mock_email_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_user_email_doc = Counter()
            self.get_email = Counter()
            self.allow_send_report_for_user = Counter()
            self.construct_message = Counter()
            self.send = Counter()
            self.update_ride_report_sent_value = Counter()

    counters = Counters()

    @patch('order_notify.repositories.email.user_email.get_user_email_doc')
    async def _get_user_email_doc(
            context: stq_context.Context,
            user_id: typing.Optional[str],
            personal_email_id: typing.Optional[str],
    ) -> typing.Optional[user_api_models.UserEmailObject]:

        counters.get_user_email_doc.call()

        if personal_email_id == NONE_EMAIL_DOC_PERSONAL_EMAIL_ID:
            return None

        if personal_email_id == NONE_PERSONAL_EMAIL_ID:
            return user_api_models.UserEmailObject(id='1')

        if personal_email_id == NOT_CONFIRMED_PERSONAL_EMAIL_ID:
            return user_api_models.UserEmailObject(
                id='3',
                confirmed=False,
                personal_email_id=NOT_CONFIRMED_PERSONAL_EMAIL_ID,
            )

        if personal_email_id == NOT_CONFIRMED_BUT_SEND_PERSONAL_EMAIL_ID:
            return user_api_models.UserEmailObject(
                id='5',
                confirmed=False,
                confirmation_code='ickqbk23h1',
                personal_email_id=NOT_CONFIRMED_BUT_SEND_PERSONAL_EMAIL_ID,
            )

        return user_api_models.UserEmailObject(
            id='3ef',
            confirmed=True,
            confirmation_code='ickqbk23h1',
            personal_email_id=CONFIRMED_PERSONAL_EMAIL_ID,
        )

    @patch(
        'order_notify.repositories.email.allowed_unconfirmed.'
        'allow_send_report_for_user',
    )
    async def _allow_send_report_for_user(
            context: stq_context.Context,
            email_doc: user_api_models.UserEmailObject,
            order_data: OrderData,
    ) -> bool:
        counters.allow_send_report_for_user.call()

        if email_doc.personal_email_id in (
                CONFIRMED_PERSONAL_EMAIL_ID,
                NOT_CONFIRMED_BUT_SEND_PERSONAL_EMAIL_ID,
        ):
            return True
        return False

    @patch('order_notify.repositories.personal.get_email')
    async def _get_email(
            context: stq_context.Context, personal_email_id: str,
    ) -> str:
        counters.get_email.call()
        return 's@yandex-team.ru'

    @patch('order_notify.repositories.email.message._construct_message')
    async def _construct_message(
            context: stq_context.Context,
            email: str,
            order_data: OrderData,
            locale: str,
            confirmation_code: typing.Optional[str] = None,
            corp_client: typing.Optional[corp_clients_models.Client] = None,
    ):
        assert email == 's@yandex-team.ru'
        assert confirmation_code == 'ickqbk23h1'
        counters.construct_message.call()
        return Message(
            campaign_slug='template_data.country_data.campaign_slug',
            from_name='template_data.locale_data.from_name',
            from_email='template_data.locale_data.from_email',
            to_email=email,
            template_vars={},
        )

    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _handle_sender(
            campaign_slug,
            from_name,
            from_email,
            to_email,
            template_vars,
            is_async,
    ):
        counters.send.call()

    @patch(
        'order_notify.repositories.ride_report_sent.'
        'update_ride_report_sent_value',
    )
    async def _update_ride_report_sent_value(
            context: stq_context.Context, order_id: str, value: bool,
    ):
        assert order_id == '5'
        assert value is True
        counters.update_ride_report_sent_value.call()

    return counters


@pytest.mark.parametrize(
    'personal_email_id, expected_times_called',
    [
        pytest.param(
            NONE_EMAIL_DOC_PERSONAL_EMAIL_ID,
            [1, 0, 0, 0, 0, 0],
            id='None_email_doc->not_send',
        ),
        pytest.param(
            NONE_PERSONAL_EMAIL_ID,
            [1, 0, 0, 0, 0, 0],
            id='None_email_doc.personal_email_id->not_send',
        ),
        pytest.param(
            NOT_CONFIRMED_PERSONAL_EMAIL_ID,
            [1, 1, 0, 0, 0, 0],
            id='not_confirmed_personal_email_id->not_send',
        ),
        pytest.param(
            NOT_CONFIRMED_BUT_SEND_PERSONAL_EMAIL_ID,
            [1, 1, 1, 1, 1, 1],
            id='not_confirmed_personal_email_id_but_allow_send->send',
        ),
        pytest.param(
            CONFIRMED_PERSONAL_EMAIL_ID,
            [1, 1, 1, 1, 1, 1],
            id='confirmed_personal_email_id->send',
        ),
    ],
)
async def test_send_user_report_mail(
        stq3_context: stq_context.Context,
        mock_functions,
        personal_email_id,
        expected_times_called,
):
    await send_report_functions.send_user_report_mail(
        context=stq3_context,
        order_data=OrderData(
            brand='', country='', order={}, order_proc={'_id': '5'},
        ),
        locale='ru',
        personal_email_id=personal_email_id,
    )

    times_called = [
        mock_functions.get_user_email_doc.times_called,
        mock_functions.allow_send_report_for_user.times_called,
        mock_functions.get_email.times_called,
        mock_functions.construct_message.times_called,
        mock_functions.send.times_called,
        mock_functions.update_ride_report_sent_value.times_called,
    ]
    assert times_called == expected_times_called
