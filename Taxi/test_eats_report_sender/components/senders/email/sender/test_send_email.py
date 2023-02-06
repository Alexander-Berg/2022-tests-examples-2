import asynctest
import pytest

from eats_report_sender.components.senders.email_sender import email_sender
from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)
from eats_report_sender.services import mds3_service
from eats_report_sender.services import personal_service
from eats_report_sender.services import sticker_service
from eats_report_sender.services.template_service import template_service


class MockedMDS3Service(mds3_service.MDS3Service):
    async def get_files_list(self, *args, **kwargs):  # pylint: disable=W0221
        return ['directory/file_1.json', 'directory/file_2.json']

    async def get_files_as_links(  # pylint: disable=W0221
            self, *args, **kwargs,
    ):
        return [
            'http://s3.yandex.ru/bucket/directory/'
            'file_1.json?expire_at=123&signed=A021bFc',
            'http://s3.yandex.ru/bucket/directory/'
            'file_2.json?expire_at=123&signed=A021bFc',
        ]

    async def get_files_as_base64(  # pylint: disable=W0221
            self, *args, **kwargs,
    ):
        return [
            mds3_service.Base64File(
                key='/directory/file_1.json', data='Y29udGVudCBvZiBmaWxlIDE=',
            ),
            mds3_service.Base64File(
                key='/directory/file_2.json',
                data='dG90YWxseSBhbm90aGVyIGZpbGUgY29udGVudA==',
            ),
        ]


class MockedPersonalService(personal_service.PersonalService):
    async def get_personal_ids(self, *args, **kwargs):  # pylint: disable=W0221
        return {'email1@email.com': 'id1', 'email2@email.com': 'id2'}


class MockedConfigTemplateService(template_service.ConfigTemplateService):
    pass


class MockedStickerService(sticker_service.StickerService):
    def get_personal_service(self):
        return MockedPersonalService(self.app_context, self.report)

    send = asynctest.CoroutineMock()


class MockedReportSender(email_sender.ReportSender):
    def get_mds3_service(self):
        return MockedMDS3Service(self.app_context, self.report)

    def get_template_service(self):
        return MockedConfigTemplateService(self.app_context, self.report)

    def get_email_sender_service(self):
        return MockedStickerService(self.app_context, self.report)


@pytest.mark.parametrize(
    'with_attachments, report_id, brand_id, expected_json',
    [
        (
            True,
            'with_attachments',
            'brand_id_with_attachments',
            'expected_request_to_sticker_with_attachments.json',
        ),
        (
            False,
            'without_attachments',
            'brand_id_without_attachments',
            'expected_request_to_sticker_without_attachments.json',
        ),
    ],
)
async def test_send_email(
        with_attachments,
        report_id,
        brand_id,
        expected_json,
        load_json,
        stq3_context,
        mock_sticker,
        mock_personal,
        mockserver,
        monkeypatch,
):

    report = api_module.Report.deserialize(
        load_json('report_data.json')[report_id],
    )
    sender = MockedReportSender(stq3_context, report)

    await sender.send()

    mocked_send = sender.email_sender_service.send
    assert mocked_send.call_args[0][0] == [
        'email1@email.com',
        'email2@email.com',
    ]

    expected_sticker_request = load_json(expected_json)
    assert mocked_send.call_args[0][1] == expected_sticker_request['body']

    assert mocked_send.call_args[0][2] == [
        mds3_service.Base64File(key=item['key'], data=item['data'])
        for item in expected_sticker_request['attachments']
    ]
