# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import (
    manager_request_accepted_notice as manager_notice,
)
from corp_notices.util import rus_mapping

pytestmark = [
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'TaxiManagerRequestAcceptedNotice': {
                'enabled': True,
                'moderator_emails': {'rus': ['docs_emails@yandex-team.ru']},
                'slugs': {'rus': 'AAAAAA'},
            },
        },
    ),
]


@pytest.fixture
def broker(cron_context):
    broker_cls = manager_notice.TaxiManagerRequestAcceptedNoticeBroker

    return broker_cls.make(
        cron_context,
        notice_kwargs={
            'manager_login': 'manager_login',
            'manager_name': 'Иван Иванов @manager',
            'country': 'rus',
            'status': 'accepted',
            'service': 'taxi',
            'enterprise_name_short': 'enterprise_name_short',
            'enterprise_name_full': 'enterprise_name_full',
            'contract_type': 'prepaid',
            'company_tin': 'company_tin',
            'company_cio': 'company_cio',
            'kbe': 'kbe',
            'city': 'moscow',
            'legal_address': 'legal_address',
            'mailing_address': 'mailing_address',
            'contacts': [{'name': 'name', 'email': 'email', 'phone': 'phone'}],
            'bank_account_number': 'bank_account_number',
            'bank_name': '',
            'bank_bic': 'bank_bic',
            'signer_name': 'signer_name',
            'signer_position': 'signer_position',
            'signer_duly_authorized': 'power_of_attorney',
            'attachments': [{'url': 'url', 'filename': 'filename'}],
            'crm_link': 'crm_link',
            'st_link': 'st_link',
            'client_login': 'client_login',
            'billing_external_id': 'billing_external_id',
            'billing_client_id': 'billing_client_id',
            'billing_person_id': 'billing_person_id',
            'billing_contract_id': 'billing_contract_id',
            'additional_information': '',
        },
    )


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() == {
        'manager_name': 'Иван Иванов @manager',
        'country': 'rus',
        'status': rus_mapping.RUS_MAPPING['status'][
            broker.notice.notice_kwargs['status']
        ],
        'service': rus_mapping.RUS_MAPPING['service'][
            broker.notice.notice_kwargs['service']
        ],
        'enterprise_name_short': 'enterprise_name_short',
        'enterprise_name_full': 'enterprise_name_full',
        'contract_type': rus_mapping.RUS_MAPPING['contract_type'][
            broker.notice.notice_kwargs['contract_type']
        ],
        'company_tin': 'company_tin',
        'company_cio': 'company_cio',
        'kbe': 'kbe',
        'city': 'moscow',
        'legal_address': 'legal_address',
        'mailing_address': 'mailing_address',
        'contacts': [{'name': 'name', 'email': 'email', 'phone': 'phone'}],
        'bank_account_number': 'bank_account_number',
        'bank_name': '',
        'bank_bic': 'bank_bic',
        'signer_name': 'signer_name',
        'signer_position': 'signer_position',
        'signer_duly_authorized': rus_mapping.RUS_MAPPING[
            'signer_duly_authorized'
        ][broker.notice.notice_kwargs['signer_duly_authorized']],
        'crm_link': 'crm_link',
        'st_link': 'st_link',
        'client_login': 'client_login',
        'billing_external_id': 'billing_external_id',
        'billing_client_id': 'billing_client_id',
        'billing_person_id': 'billing_person_id',
        'billing_contract_id': 'billing_contract_id',
        'attachments': [{'url': 'url', 'filename': 'filename'}],
        'additional_information': '',
    }


async def test_emails(broker):
    assert await broker.get_emails() == [
        'manager_login@yandex-team.ru',
        'docs_emails@yandex-team.ru',
    ]


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('TaxiManagerRequestAcceptedNotice')
    assert registry.get('CargoManagerRequestAcceptedNotice')
    assert registry.get('TaxiManagerRequestRejectedNotice')
    assert registry.get('CargoManagerRequestRejectedNotice')
