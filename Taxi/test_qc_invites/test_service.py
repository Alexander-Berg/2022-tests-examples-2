import uuid

from aiohttp import web
import pytest

from qc_invites.generated.cron import run_cron
from test_qc_invites.helpers import consts as test_consts
from test_qc_invites.helpers import fixtures
from test_qc_invites.helpers import mocks


def stub_services(mockserver):
    """Ставит заглушку на неиспользуемые ручки"""

    @mockserver.json_handler('/quality-control/api/v1/pass/data')
    def _qc_pass_data_handler(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_handler(request):
        return {'parks': []}

    @mockserver.handler('/communications/driver/notification/bulk-push')
    def _push_handler(request):
        return web.json_response(status=200, content_type='text/plain')


async def get_invite_status(taxi_qc_invites_web, invite_id):
    response = await taxi_qc_invites_web.get(
        test_consts.INVITE_INFO_URL, params={'invite_id': invite_id},
    )
    assert response.status == 200
    data = await response.json()
    return data['status']


async def get_invite_entities(taxi_qc_invites_web, invite_id):
    response = await taxi_qc_invites_web.get(
        test_consts.INVITE_ENTITIES_URL, params={'invite_id': invite_id},
    )
    assert response.status == 200
    data = await response.json()
    return data['items']


@pytest.mark.parametrize(['body'], fixtures.TEST_FULL_SERVICE_ROUTE_BODY)
@pytest.mark.parametrize(['exam'], fixtures.TEST_FULL_SERVICE_ROUTE_EXAM)
async def test_full_service_route(taxi_qc_invites_web, body, exam, mockserver):
    """Тестируем полный цикл работы сервиса (при условии, что нет ошибок)"""
    body['exam'] = exam
    park_id, car_id, pass_id, driver_id, license_pd_id = [
        uuid.uuid4().hex for i in range(5)
    ]

    # мокаем ответ от сервиса пд
    mocks.mock_personal_license_find(mockserver, license_pd_id)
    mocks.mock_fleet_vehicles_retrieve(mockserver, park_id, car_id)
    mocks.mock_driver_profiles_retrieve(mockserver, park_id, car_id, driver_id)
    mocks.mock_qc_state(mockserver, park_id, car_id, pass_id)
    mocks.mock_qc_settings(mockserver)
    stub_services(mockserver)

    # Делаем запрос на вызов
    response = await taxi_qc_invites_web.post(
        test_consts.INVITE_URL, json=body, headers={'X-Yandex-Uid': 'uid'},
    )
    assert response.status == 200
    invite_id = (await response.json())['invite_id']

    # Подготавливаем вызовы
    await run_cron.main(
        ['qc_invites.crontasks.prepare_invites_driver', '-t', '0'],
    )

    # Чекаем, что вызов перешёл в состояние 'prepared'
    status = await get_invite_status(taxi_qc_invites_web, invite_id)
    assert status == 'prepared'

    # Вызываем
    await run_cron.main(['qc_invites.crontasks.invite_entities', '-t', '0'])

    # Проверяем вызванные сущности
    items = await get_invite_entities(taxi_qc_invites_web, invite_id)
    assert items[0]['invited']
