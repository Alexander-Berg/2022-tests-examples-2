import pytest

from tests_bank_applications import common
from tests_bank_applications.product import db_helpers

HANDLE_URL = '/v1/applications/v1/product/get_application_status'
SUPPORT_URL = {'support_url': 'http://support.ya/'}
STATUSES_LIST = {
    'PRODUCT': {
        'FAILED': {'title': 'Upal'},
        'PROCESSING': {
            'title': 'Ваш телефон в обработке!',
            'description': (
                'Обрабатывается! А пока можешь закинуть до 15.000 рублей'
            ),
        },
    },
}
APP_TYPE = 'PRODUCT'


@pytest.mark.config(BANK_APPLICATIONS_STATUS_TITLES=STATUSES_LIST)
@pytest.mark.parametrize(
    'status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_status(taxi_bank_applications, pgsql, status):
    application_id = db_helpers.insert_application(pgsql, status=status)

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.default_headers(),
        json={'application_id': application_id},
    )

    if status == 'SUCCESS':
        assert response.status_code == 200
        assert response.json() == {'status': status}
    elif status == 'FAILED':
        assert response.status_code == 200
        assert response.json() == {
            'status': status,
            'title': STATUSES_LIST[APP_TYPE][status]['title'],
            'support_url': SUPPORT_URL['support_url'],
        }
    elif status == 'PROCESSING':
        assert response.status_code == 200
        assert response.json() == {
            'status': status,
            'title': STATUSES_LIST[APP_TYPE][status]['title'],
            'description': STATUSES_LIST[APP_TYPE][status]['description'],
            'support_url': SUPPORT_URL['support_url'],
        }
    elif status == 'CREATED':
        assert response.status_code == 404


async def test_wrong_user_id(taxi_bank_applications, pgsql):
    application_id = db_helpers.insert_application(
        pgsql, common.TEST_ONE_YANDEX_BUID, common.STATUS_PROCESSING,
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.default_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404
