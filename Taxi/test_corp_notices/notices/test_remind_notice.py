# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices import base
from corp_notices.notices.notices import remind_prepaid_notice as remind_notice

pytestmark = [
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'FirstRemindPrepaidNotice': {
                'enabled': True,
                'slugs': {'rus': 'AAAAAA'},
                'days_offset': 3,
            },
        },
    ),
]


MOCK_CLIENT_RESPONSE = {
    'id': 'client_id_1',
    'name': 'Test client',
    'billing_name': 'None',
    'country': 'rus',
    'yandex_login': 'test-client',
    'description': 'Test',
    'is_trial': False,
    'email': 'test@email.com',
    'features': [],
    'billing_id': '101',
    'created': '2020-01-01T03:00:00+03:00',
}


MOCK_SERVICE_TAXI_RESPONSE = {
    'is_active': True,
    'is_visible': True,
    'is_test': False,
    'deactivate_threshold_ride': 1000,
    'comment': 'comment',
    'categories': [],
    'default_category': 'abc',
}


@pytest.fixture
def broker(cron_context):
    broker_cls = remind_notice.FirstRemindPrepaidNoticeBroker

    return broker_cls.make(cron_context, client_id='client_id_1')


async def test_pre_send_check_failed(broker, mock_corp_clients):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE
    try:
        await broker.pre_send()
        assert False
    except base.SendNoticeCheckFailed:
        assert True


async def test_pre_send_check_passed(broker, mock_corp_clients):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE
    mock_corp_clients.data.get_service_taxi_response = (
        MOCK_SERVICE_TAXI_RESPONSE
    )
    await broker.pre_send()


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('FirstRemindPrepaidNotice')
    assert registry.get('SecondRemindPrepaidNotice')
    assert registry.get('ThirdRemindPrepaidNotice')
    assert registry.get('ThirdRemindOfferNotice')
