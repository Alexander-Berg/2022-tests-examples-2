import pytest

from eats_report_sender.components import report_sender_config
from eats_report_sender.components.senders import email_sender
from eats_report_sender.components.senders import exceptions
from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


EmailSender = email_sender.EmailSender


async def test_should_raise_exception_if_cannot_find_email(
        load_json, stq3_context, mockserver,
):
    @mockserver.handler('/personal/v1/emails/bulk_store')
    async def _personal_emails_mocks(request, **kwargs):
        return mockserver.make_response(
            json={
                'items': [
                    {'id': 'id1', 'value': 'email1@email.com'},
                    {'id': 'id2', 'value': 'email2@email.com'},
                ],
            },
        )

    with pytest.raises(exceptions.CannotFindBrandEmailException):
        await stq3_context.email_sender.send(
            api_module.Report.deserialize(
                load_json('report_data.json')['without_email'],
            ),
        )


async def test_should_raise_exception_if_cannot_find_email_settings(
        load_json, stq3_context,
):
    with pytest.raises(
            report_sender_config.CannotFindBrandEmailSettingsException,
    ):
        await stq3_context.email_sender.send(
            api_module.Report.deserialize(
                load_json('report_data.json')['without_email_settings'],
            ),
        )
