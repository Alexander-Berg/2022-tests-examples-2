# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import trial_client_notice


@pytest.fixture
def broker(cron_context):
    encrypted_pass = cron_context.corp_crypto.encrypt('Qw123456')

    return trial_client_notice.NewTrialAutoregClientNoticeBroker.make(
        cron_context,
        notice_kwargs={
            'yandex_login': 'test_login',
            'contract_type': 'taxi',
            'encrypted_password': encrypted_pass,
        },
    )


async def test_template_kwargs(broker):
    assert await broker.get_template_kwargs() == {
        'Login': 'test_login',
        'Pass': 'Qw123456',
        'contract_type': 'taxi',
    }


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('NewTrialAutoRegisteredClientNotice')
