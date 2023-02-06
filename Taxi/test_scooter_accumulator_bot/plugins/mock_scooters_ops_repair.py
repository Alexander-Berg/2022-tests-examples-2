import uuid

import aiohttp.web
import pytest


def scooters_ops_repair_repair_start(request):  # pylint: disable=C0103
    assert request.method == 'POST'
    return (
        200,
        {
            'repair_id': str(uuid.uuid4()),
            'performer_id': request.json['performer_id'],
            'depot_id': request.json['depot_id'],
            'vehicle_id': request.json['vehicle_id'],
            'started_at': '2022-04-01T07:05:00+00:00',
            'status': 'started',
            'vehicle_info': {'mileage': 370.39},
            'jobs': [],
        },
    )


def scooters_ops_repair_repair_stop(request):  # pylint: disable=C0103
    assert request.method == 'POST'
    return (200, {})


def scooters_ops_repair_repair_job_start(request):  # pylint: disable=C0103
    assert request.method == 'POST'

    return (
        200,
        {
            'job_id': str(uuid.uuid4()),
            'started_at': '2022-04-01T07:05:00+00:00',
            'status': 'started',
            'type': request.json['type'],
        },
    )


def scooters_ops_repair_repair_job_stop(request):  # pylint: disable=C0103
    assert request.method == 'POST'
    return (200, {})


@pytest.fixture
def scooter_accumulator_bot_scooters_ops_repair_mocks(
        mock_scooters_ops_repair,
):  # pylint: disable=C0103
    @mock_scooters_ops_repair('/scooters-ops-repair/v1/repair/start')
    async def _repair_start(request):
        code, tackles = scooters_ops_repair_repair_start(request)
        return aiohttp.web.json_response(tackles, status=code)

    @mock_scooters_ops_repair('/scooters-ops-repair/v1/repair/stop')
    async def _repair_stop(request):
        code, tackles = scooters_ops_repair_repair_stop(request)
        return aiohttp.web.json_response(tackles, status=code)

    @mock_scooters_ops_repair('/scooters-ops-repair/v1/repair-job/start')
    async def _repair_job_start(request):
        code, tackles = scooters_ops_repair_repair_job_start(request)
        return aiohttp.web.json_response(tackles, status=code)

    @mock_scooters_ops_repair('/scooters-ops-repair/v1/repair-job/stop')
    async def _repair_job_stop(request):
        code, tackles = scooters_ops_repair_repair_job_stop(request)
        return aiohttp.web.json_response(tackles, status=code)
