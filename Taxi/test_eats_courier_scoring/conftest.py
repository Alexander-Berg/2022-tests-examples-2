# pylint: disable=redefined-outer-name,invalid-name
import datetime
from typing import Dict

import pytest

from taxi.clients import startrack

from eats_courier_scoring.common import entities
import eats_courier_scoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_courier_scoring.generated.service.pytest_plugins']


@pytest.fixture
def patch_create_startrack_ticket(patch_aiohttp_session, response_mock):
    def wrapper(response, raise_exception=False):
        @patch_aiohttp_session(
            'https://st-api.test.yandex-team.ru/v2/issues/', 'POST',
        )
        def get_tickets(*args, **kwargs):
            if raise_exception:
                raise startrack.BaseError()
            return response_mock(json=response)

        return get_tickets

    return wrapper


@pytest.fixture
def mock_driver_wall_add(mock_driver_wall):
    def _mock_driver_wall_add(*, check_request_drivers: list = None):
        @mock_driver_wall('/internal/driver-wall/v1/add')
        def _(request):
            assert request.json['service'] == 'contractor-quality-report'
            if check_request_drivers:
                assert check_request_drivers == request.json['drivers']
            return {'id': request.json['id']}

    return _mock_driver_wall_add


@pytest.fixture
def mock_blocklist_add(mock_blocklist):
    def _mock_blocklist_add():
        @mock_blocklist('/internal/blocklist/v1/add')
        def _(request):
            return {'block_id': 'block_id'}

    return _mock_blocklist_add


def create_exp3_response(
        courier_id: int,
        enabled: bool = True,
        punishment_names: list = None,
        defect_scores: list = None,
):
    return pytest.mark.client_experiments3(
        consumer='eats-courier-scoring/defects_scoring',
        config_name='eats_courier_scoring_defects_scoring',
        args=[
            {
                'name': 'driver_profile_id',
                'type': 'string',
                'value': str(courier_id),
            },
            {'name': 'region_name', 'type': 'string', 'value': 'region'},
        ],
        value={
            'enabled': enabled,
            'punishment_names': punishment_names or [],
            'defect_scores': defect_scores or [],
        },
    )


@pytest.fixture(autouse=True)
def _default_external_mock(
        mock_blocklist_add,
        mock_driver_wall_add,
        patch_create_startrack_ticket,
):
    mock_blocklist_add()
    mock_driver_wall_add()
    patch_create_startrack_ticket({})


@pytest.fixture
def patch_load_couriers_and_defects(patch):
    def _patch_load_couriers_and_defects(courier_ids):
        @patch(
            'eats_courier_scoring.common.greenplum'
            '.GreenplumDefectOrdersContext.load_couriers_and_defects',
        )
        async def _(*args, **kwargs):
            couriers = [
                create_courier_model(courier_id) for courier_id in courier_ids
            ]
            defects = [
                entities.Defect(
                    courier_id=courier_id,
                    order_id=order_id,
                    order_nr='order_nr',
                    defect_type=entities.DefectType('damaged_order'),
                    defect_dttm=datetime.datetime(2022, 4, 1),
                    crm_comment='0',
                    our_refund_total_lcy=0,
                    incentive_refunds_lcy=0,
                    incentive_rejected_order_lcy=0,
                )
                for order_id, courier_id in enumerate(courier_ids)
            ]
            return couriers, defects

    return _patch_load_couriers_and_defects


@pytest.fixture
def patch_get_active_couriers_count_by_region(patch):
    def _patch_get_active_couriers_count_by_region(response: Dict[str, int]):
        @patch(
            'eats_courier_scoring.common.greenplum'
            '.GreenplumDefectOrdersContext.load_active_couriers_by_region',
        )
        async def _(*args, **kwargs):
            return response

    return _patch_get_active_couriers_count_by_region


def create_courier_model(
        courier_id, n_orders_last_period=1, region='region', region_id=1,
):
    return entities.CourierModel(
        courier_id=courier_id,
        courier_username=f'courier_username_{courier_id}',
        courier_type='courier_type',
        work_status='work_status',
        pool_name='pool_name',
        region_id=region_id,
        region_name=region,
        n_orders_last_period=n_orders_last_period,
        courier_uuid=str(courier_id),
        courier_dbid=str(courier_id),
        driver_license_pd_id=f'license_id_{courier_id}',
        date_last_order=datetime.datetime.utcnow(),
        date_first_order=datetime.datetime.utcnow(),
    )


def create_defect(
        courier_id: int,
        order_id: int,
        defect_type: entities.DefectType = entities.DefectType(
            'damaged_order',
        ),
) -> entities.Defect:
    return entities.Defect(
        courier_id=courier_id,
        order_id=order_id,
        order_nr=f'order_nr_{order_id}',
        defect_type=defect_type,
        defect_dttm=datetime.datetime.utcnow(),
        crm_comment='0',
        our_refund_total_lcy=0,
        incentive_refunds_lcy=0,
        incentive_rejected_order_lcy=0,
    )


class DiffCountPunishments:
    def __init__(self, context, correct_diff: int):
        self.context = context
        self.correct_diff = correct_diff
        self.start_count = 0

    async def __aenter__(self):
        self.start_count = await self.count_punishments()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        finish_count = await self.count_punishments()
        diff = finish_count - self.start_count
        assert self.correct_diff == diff, f'Incorrect diff punishments'

    async def count_punishments(self):
        async with self.context.pg.master.acquire() as connection:
            return await connection.fetchval(
                'SELECT count(*) FROM eats_courier_scoring.punishments p '
                'INNER JOIN eats_courier_scoring.punishment_additional_info ai'
                ' ON p.id=ai.punishment_id',
            )


class DiffCountPunishmentsByName:
    def __init__(self, context, correct_diffs: Dict[str, int]):
        self.context = context
        self.correct_diffs = correct_diffs
        self.start_counts: Dict[str, int] = {}

    async def __aenter__(self):
        for punishment_name in self.correct_diffs:
            self.start_counts[punishment_name] = await self.count_punishments(
                punishment_name,
            )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for punishment_name, correct_diff in self.correct_diffs.items():
            start_count = self.start_counts[punishment_name]
            finish_count = await self.count_punishments(punishment_name)
            diff = finish_count - start_count
            assert correct_diff == diff, f'Incorrect diff {punishment_name}'

    async def count_punishments(self, punishment_name: str):
        async with self.context.pg.master.acquire() as connection:
            return await connection.fetchval(
                'SELECT count(*) FROM eats_courier_scoring.punishments p '
                'INNER JOIN eats_courier_scoring.punishment_additional_info ai'
                ' ON p.id=ai.punishment_id'
                ' WHERE p.punishment_name = $1',
                punishment_name,
            )
