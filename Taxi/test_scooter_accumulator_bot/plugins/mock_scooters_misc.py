import aiohttp.web
import pytest


def scooters_misc_tackles_tackle(request):
    assert request.method == 'GET'

    if request.query['id'] == 'daba':
        return (
            200,
            {
                'tackle': {
                    'id': 'daba',
                    'kind': 'recharging_wire',
                    'depot_id': 'fake:yandex_red_rose',
                    'version': 12,
                },
            },
        )

    if request.query['id'] == 'naf-naf':
        return (
            200,
            {
                'tackle': {
                    'id': 'naf-naf',
                    'kind': 'recharging_wire',
                    'depot_id': 'depot_id1',
                    'version': 1,
                },
            },
        )

    return 404, {}


def scooters_misc_tackles_list(request):
    assert request.method == 'GET'

    if 'recharge_task_id' in request.query:
        if request.query['recharge_task_id'] == 'recharge_task_id1':
            return (
                200,
                {
                    'tackles': [
                        {
                            'id': 'naf-naf',
                            'kind': 'recharging_wire',
                            'depot_id': 'depot_id1',
                            'version': 1,
                        },
                    ],
                },
            )
        return 404, {}

    return (
        200,
        {
            'tackles': [
                {
                    'id': 'daba',
                    'kind': 'recharging_wire',
                    'depot_id': 'fake:yandex_red_rose',
                    'version': 12,
                },
                {
                    'id': 'naf-naf',
                    'kind': 'recharging_wire',
                    'depot_id': 'depot_id1',
                    'version': 1,
                },
            ],
        },
    )


def scooters_misc_tackles_drop(request):
    assert request.method == 'POST'

    if request.query['id'] != 'daba':
        return 404, {}

    return (
        200,
        {'tackle': {'id': 'daba', 'kind': 'recharging_wire', 'version': 12}},
    )


def scooters_misc_tackles_update(request):
    assert request.method == 'POST'

    if request.query['id'] != 'daba' and request.query['id'] != 'naf-naf':
        return 404, {}

    return (
        200,
        {
            'tackle': {
                'id': request.query['id'],
                'kind': 'recharging_wire',
                'depot_id': request.json['depot_id'],
                'version': 12,
            },
        },
    )


def scooters_misc_tackle_assign(request):
    assert request.method == 'POST'

    if (
            'performer_id' in request.query
            and request.query['performer_id']
            == '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c'  # noqa: E501 line too long
            and 'id' in request.query
            and request.query['id'] == 'naf-naf'
    ):
        return 200, {}

    return 404, {}


def scooters_misc_tackle_release(request):
    assert request.method == 'POST'

    if (
            'performer_id' in request.query
            and request.query['performer_id']
            == '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c'  # noqa: E501 line too long
            and 'id' in request.query
            and request.query['id'] == 'naf-naf'
    ):
        return 200, {}

    return 404, {}


def scooters_misc_recharge_task(request):
    assert request.method == 'GET'

    if (
            request.query['performer_id']
            == '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c'  # noqa: E501 line too long
    ):
        return (
            200,
            {
                'recharge_task': {
                    'id': 'recharge_task_id1',
                    'type': 'dead',
                    'status': 'created',
                    'performer_id': '5434bf074f8d4239a3a8960416525a10_11e6391c3d2a4673819d1fafe70d982c',  # noqa: E501 line too long
                    'cargo_claim_id': 'cargo_claim_id1',
                },
            },
        )

    return 404, {}


def scooters_misc_service_vehicle_info(request):  # pylint: disable=C0103
    assert request.method == 'GET'

    if request.query['vehicle_id'] == '0d00b5b3-93fd-49f0-91a4-12f7eaec46e7':
        return (
            200,
            {
                'firmware': {
                    'iot': 'R06A05V02',
                    'ecu': '4401',
                    'ble': 'R00A03V02',
                },
                'sensors': {'mileage': 350.00},
                'repairs': [
                    {
                        'mileage': 100.0,
                        'completed_at': '2022-06-10T09:25:04.941465+00:00',
                        'jobs': ['brake_adjustment', 'fender_replacement'],
                    },
                    {
                        'mileage': 300.00,
                        'completed_at': '2022-06-14T11:13:38.085384+00:00',
                        'jobs': ['stickers_change'],
                    },
                ],
                'complains': ['Не тормозит', 'Сломался руль'],
            },
        )

    return 404, {}


def scooters_misc_vehicle_control(request):
    assert request.method == 'POST'

    return 200, {}


def scooters_misc_admin_v1_depots_list(request):  # pylint: disable=C0103
    assert request.method == 'POST'
    if request.json['depot_id'] == 'test':
        return (
            200,
            {
                'depots': [
                    {
                        'depot_id': 'test',
                        'created_at': '2022-03-23T12:39:27.13368+00:00',
                        'updated_at': '2022-03-23T12:40:04.502278+00:00',
                        'location': {'lon': 42.0, 'lat': 35.0},
                        'city': 'best_city',
                        'cabinets': [],
                        'address': 'best_Adress',
                        'enabled': True,
                        'timetable': [],
                        'allowed_from_areas': [],
                    },
                ],
            },
        )

    return 404, {'depots': []}


@pytest.fixture
def scooter_accumulator_bot_scooters_misc_mocks(
        mock_scooters_misc,
):  # pylint: disable=C0103
    @mock_scooters_misc('/v1/tackles/list')
    async def _tackles_list(request):
        code, tackles = scooters_misc_tackles_list(request)
        return aiohttp.web.json_response(tackles, status=code)

    @mock_scooters_misc('/v1/tackles/depot/drop')
    async def _tackles_depot_drop_post(request):
        code, tackle = scooters_misc_tackles_drop(request)
        return aiohttp.web.json_response(tackle, status=code)

    @mock_scooters_misc('/v1/tackles/depot/update')
    async def _tackles_depot_update_post(request):
        code, tackle = scooters_misc_tackles_update(request)
        return aiohttp.web.json_response(tackle, status=code)

    @mock_scooters_misc('/v1/tackles/tackle')
    async def _tackles_tackle_get(request):
        code, tackle = scooters_misc_tackles_tackle(request)
        return aiohttp.web.json_response(tackle, status=code)

    @mock_scooters_misc('/v1/tackles/assign')
    async def _tackles_assign_post(request):
        code, tackle = scooters_misc_tackle_assign(request)
        return aiohttp.web.json_response(tackle, status=code)

    @mock_scooters_misc('/v1/tackles/release')
    async def _tackles_release_post(request):
        code, tackle = scooters_misc_tackle_release(request)
        return aiohttp.web.json_response(tackle, status=code)

    @mock_scooters_misc('/scooters-misc/v1/recharge-tasks/performing')
    async def _recharge_tasks_performing_post(request):
        code, recharge_tasks = scooters_misc_recharge_task(request)
        return aiohttp.web.json_response(recharge_tasks, status=code)

    @mock_scooters_misc('/scooters-misc/v1/service/vehicle-info')
    async def _service_vehicle_info_get(request):
        code, service_vehicle_info = scooters_misc_service_vehicle_info(
            request,
        )
        return aiohttp.web.json_response(service_vehicle_info, status=code)

    @mock_scooters_misc('/admin/v1/depots/list')
    async def _admin_v1_depots_list_post(request):
        code, depots = scooters_misc_admin_v1_depots_list(request)
        return aiohttp.web.json_response(depots, status=code)

    @mock_scooters_misc('/scooters-misc/v1/service/vehicle-control')
    async def _service_vehicle_control_post(request):
        code, body = scooters_misc_vehicle_control(request)
        return aiohttp.web.json_response(body, status=code)
