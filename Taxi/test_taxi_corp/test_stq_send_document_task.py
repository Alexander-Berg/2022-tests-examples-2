# pylint: disable=redefined-outer-name
import base64

import pytest

from taxi_corp import stq


@pytest.mark.parametrize(
    [
        'document',
        'email',
        'external_id',
        'country_settings',
        'client_name',
        'manager',
        'yadoc_act',
        'attachments',
        'expected_args',
    ],
    [
        pytest.param(
            {
                'doc_id': '116716',
                'doc_date': '2021-01-31',
                'doc_number': '999999999',
            },
            'client1@yandex.ru',
            '951088/20',
            {'language': 'en', 'slug': 'campaign-slug'},
            'The Boring Company',
            {
                'name': 'Lana Del Rey',
                'phone': '+7 499 705 5555',
                'mobile_phone': '',
                'extension': '67461',
                'email': 'anvchernova@ybs.yandex.ru',
                'tier': 'SMB',
            },
            b'yadoc_act',
            [
                {
                    'filename': 'act_951088/20_2021-01-31.pdf',
                    'mime_type': 'application/pdf',
                    'data': base64.b64encode(b'yadoc_act').decode(),
                },
            ],
            {
                'month': 'January',
                'client_name': 'The Boring Company',
                'contract_number': '951088/20',
                'date': '2021-01-31',
                'manager_name': 'Lana Del Rey',
                'manager_phone': '+7 499 705 5555',
                'phone_extension': '67461',
            },
            id='correct_data',
        ),
    ],
)
@pytest.mark.translations(corp={'month.01': {'en': 'January'}})
async def test_task(
        patch,
        taxi_corp_app_stq,
        document,
        email,
        external_id,
        country_settings,
        client_name,
        manager,
        yadoc_act,
        attachments,
        expected_args,
):
    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, email_data, *args, **kwargs):
        assert email_data['attachments'] == attachments
        assert email_data['args'] == str(expected_args).replace('\'', '"')

    @patch('taxi.clients.yadoc.YaDocClient.download_document')
    async def _download_document(doc_id):
        return yadoc_act

    await stq.send_document(
        taxi_corp_app_stq,
        email=email,
        external_id=external_id,
        document=document,
        country_settings=country_settings,
        client_name=client_name,
        manager=manager,
    )
