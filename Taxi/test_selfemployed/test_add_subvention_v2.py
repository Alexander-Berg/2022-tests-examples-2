import pytest

from testsuite.utils import http

from selfemployed.db import dbreceipts


@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
@pytest.mark.parametrize(
    'park_id,driver_id,has_mapping',
    [('p1', 'd1', True), ('p1', 'd1', False), ('uber_p1', 'uber_d1', True)],
)
async def test_add_subvention_old_style_profile(
        se_client, se_web_context, park_id, driver_id, has_mapping, mockserver,
):
    if not has_mapping:

        @mockserver.json_handler('/fleet-synchronizer/v1/mapping/driver')
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

    response = await se_client.post(
        '/add-subvention/v2',
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'subvention_id': 's1',
            'total': 120.1,
            'receipt_date': '2018-12-29T17:29:30.742701Z',
            'checkout_date': '2018-12-29T17:29:30.742701Z',
        },
    )
    assert response.status == 200

    pg_ = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg_, park_id)
    receipt = await dbreceipts.get_receipt(pg_, shard, 's1')

    assert receipt['status'] == 'new'
    assert receipt['inn'] == '111'
    assert receipt['park_id'] == park_id
    assert receipt['driver_id'] == driver_id


@pytest.mark.pgsql('selfemployed_main', files=['add_full_profile.sql'])
@pytest.mark.parametrize(
    'park_id,driver_id,has_mapping',
    [('p1', 'd1', True), ('p1', 'd1', False), ('uber_p1', 'uber_d1', True)],
)
async def test_add_subvention_new_style_profile(
        se_client,
        se_web_context,
        park_id,
        driver_id,
        has_mapping,
        mock_fleet_synchronizer,
        mock_personal,
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

    @mock_personal('/v1/tins/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID_1', 'primary_replica': False}
        return {'value': '01234567890', 'id': 'INN_PD_ID_1'}

    response = await se_client.post(
        '/add-subvention/v2',
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'subvention_id': 's1',
            'total': 120.1,
            'receipt_date': '2018-12-29T17:29:30.742701Z',
            'checkout_date': '2018-12-29T17:29:30.742701Z',
        },
    )
    assert response.status == 200

    pg_ = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg_, park_id)
    receipt = await dbreceipts.get_receipt(pg_, shard, 's1')

    assert receipt['status'] == 'new'
    assert receipt['inn'] == '01234567890'
    assert receipt['park_id'] == park_id
    assert receipt['driver_id'] == driver_id
    assert receipt['do_send_receipt'] is True
    assert receipt['is_own_park'] is False


async def test_add_subvention_not_selfemployed(
        se_client, se_web_context, mock_fleet_synchronizer,
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

    response = await se_client.post(
        '/add-subvention/v2',
        json={
            'park_id': 'p1',
            'driver_id': 'd1',
            'subvention_id': 's1',
            'total': 120.1,
            'receipt_date': '2018-12-29T17:29:30.742701Z',
            'checkout_date': '2018-12-29T17:29:30.742701Z',
        },
    )
    assert response.status == 200

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
async def test_add_subvention_moved_to_events(
        se_client, se_web_context, mock_fleet_synchronizer,
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

    response = await se_client.post(
        '/add-subvention/v2',
        json={
            'park_id': 'p1',
            'driver_id': 'd1',
            'subvention_id': 's1',
            'total': 120.1,
            'receipt_date': '2018-12-29T17:29:30.742701Z',
            'checkout_date': '2018-12-29T17:29:30.742701Z',
        },
    )
    assert response.status == 200

    pg_ = se_web_context.pg
    for orders in pg_.orders_masters:
        count = await orders.fetchval('SELECT COUNT(*) FROM receipts')
        assert count == 0


async def test_add_subvention_date_workaround(
        se_client, se_web_context, mock_fleet_synchronizer,
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

    response = await se_client.post(
        '/add-subvention/v2',
        json={
            'park_id': 'p1',
            'driver_id': 'd1',
            'subvention_id': 's1',
            'total': 120.1,
            'receipt_date': '0001-01-01T00:00:00.000000Z',
            'checkout_date': '0001-01-01T00:00:00.000000Z',
        },
    )
    assert response.status == 200
