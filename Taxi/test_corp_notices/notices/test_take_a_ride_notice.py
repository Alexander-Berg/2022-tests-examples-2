# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices import base
from corp_notices.notices.notices import take_a_ride_notice

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
    broker_cls = take_a_ride_notice.PrepaidFirstTakeARideNoticeBroker

    return broker_cls.make(cron_context, client_id='client_id_1')


@pytest.fixture
def second_broker(cron_context, mock_corp_clients):
    client_id = 'client_id_2'

    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE
    mock_corp_clients.data.get_client_response['id'] = client_id

    broker_cls = take_a_ride_notice.PrepaidFirstTakeARideNoticeBroker

    return broker_cls.make(cron_context, client_id=client_id)


async def test_pre_send_check_failed_orders(db, broker, mock_corp_clients):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE
    mock_corp_clients.data.get_service_taxi_response = (
        MOCK_SERVICE_TAXI_RESPONSE
    )

    try:
        await broker.pre_send()
        assert False
    except base.SendNoticeCheckFailed:
        assert broker.notice.reason == 'Client already has a successful order'


async def test_pre_send_check_failed_service(
        db, second_broker, mock_corp_clients,
):
    try:
        await second_broker.pre_send()
        assert False
    except base.SendNoticeCheckFailed:
        assert (
            second_broker.notice.reason
            == 'Client doesn\'t have a taxi service'
        )


async def test_pre_send_check_passed(db, second_broker, mock_corp_clients):
    mock_corp_clients.data.get_service_taxi_response = (
        MOCK_SERVICE_TAXI_RESPONSE
    )

    await second_broker.pre_send()


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('PrepaidFirstTakeARideNotice')
    assert registry.get('PrepaidSecondTakeARideNotice')
