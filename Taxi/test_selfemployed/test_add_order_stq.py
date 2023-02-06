import datetime

import pytest

from testsuite.utils import http

from selfemployed.db import dbreceipts


@pytest.mark.parametrize(
    'is_new_style',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.pgsql(
                    'selfemployed_main', files=['add_full_profile.sql'],
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.pgsql(
                    'selfemployed_main', files=['add_simple_profile.sql'],
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'park_id,driver_id,has_mapping',
    [('p1', 'd1', True), ('p1', 'd1', False), ('uber_p1', 'uber_d1', True)],
)
async def test_add_order(
        stq_runner,
        se_web_context,
        park_id,
        driver_id,
        has_mapping,
        mock_fleet_synchronizer,
        mock_personal,
        is_new_style,
):
    if not has_mapping:

        @mock_fleet_synchronizer('/v1/mapping/driver')
        def _mapping_driver(request):
            return {
                'mapping': [
                    {
                        'app_family': 'taximeter',
                        'park_id': 'p1',
                        'driver_id': 'd1',
                    },
                ],
            }

    if is_new_style:

        @mock_personal('/v1/tins/retrieve')
        async def _store_phone_pd(request: http.Request):
            assert request.json == {
                'id': 'INN_PD_ID_1',
                'primary_replica': False,
            }
            return {'value': '111', 'id': 'INN_PD_ID_1'}

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_add_order.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            alias_id='o1',
            performer_dbid=park_id,
            performer_uuid=driver_id,
            order_finished_at=datetime.datetime.fromisoformat(
                '2018-12-29T17:29:30.742701+00:00',
            ),
            cost=110.5,
            payment_tech_type='card',
        ),
    )

    pg_ = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg_, park_id)
    receipt = await dbreceipts.get_receipt(pg_, shard, 'o1')

    assert receipt['status'] == 'new'
    assert receipt['inn'] == '111'
    assert receipt['park_id'] == park_id
    assert receipt['driver_id'] == driver_id
    assert receipt['do_send_receipt'] is True
    assert receipt['is_own_park'] != is_new_style


@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
async def test_add_order_duplicate(stq_runner):
    kwargs = dict(
        alias_id='o1',
        performer_dbid='p1',
        performer_uuid='d1',
        order_finished_at=datetime.datetime.fromisoformat(
            '2018-12-29T17:29:30.742701+00:00',
        ),
        cost=110.5,
        payment_tech_type='card',
    )

    # Order added for the first time
    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_add_order.call(
        task_id='task_id_1', args=(), kwargs=kwargs,
    )

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_add_order.call(
        task_id='task_id_1', args=(), kwargs=kwargs,
    )


async def test_add_order_not_selfemployed(
        stq_runner, se_web_context, mock_fleet_synchronizer,
):
    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {
            'mapping': [
                {
                    'app_family': 'taximeter',
                    'park_id': 'p1',
                    'driver_id': 'd1',
                },
            ],
        }

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_add_order.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            alias_id='o1',
            performer_dbid='p1',
            performer_uuid='d1',
            order_finished_at=datetime.datetime.fromisoformat(
                '2018-12-29T17:29:30.742701+00:00',
            ),
            cost=110.5,
            payment_tech_type='card',
        ),
    )

    pg_ = se_web_context.pg
    for orders in pg_.orders_masters:
        count = await orders.fetchval('SELECT COUNT(*) FROM receipts')
        assert count == 0


@pytest.mark.client_experiments3(
    consumer='selfemployed/fns-se/billing-events',
    experiment_name='pro_fns_selfemployment_use_billing_events',
    args=[{'name': 'park_id', 'type': 'string', 'value': 'p1'}],
    value={'use_old_style': False},
)
async def test_add_order_moved_to_events(
        stq_runner, se_web_context, mock_fleet_synchronizer,
):
    @mock_fleet_synchronizer('/v1/mapping/driver')
    def _mapping_driver(request):
        return {
            'mapping': [
                {
                    'app_family': 'taximeter',
                    'park_id': 'p1',
                    'driver_id': 'd1',
                },
            ],
        }

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_add_order.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            alias_id='o1',
            performer_dbid='p1',
            performer_uuid='d1',
            order_finished_at=datetime.datetime.fromisoformat(
                '2018-12-29T17:29:30.742701+00:00',
            ),
            cost=110.5,
            payment_tech_type='card',
        ),
    )

    pg_ = se_web_context.pg
    for orders in pg_.orders_masters:
        count = await orders.fetchval('SELECT COUNT(*) FROM receipts')
        assert count == 0
