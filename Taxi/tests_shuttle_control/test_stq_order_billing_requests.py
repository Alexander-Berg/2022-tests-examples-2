# pylint: disable=import-only-modules
import datetime

import pytest

from tests_shuttle_control.utils import select_named


class AnyDateTime:
    def __eq__(self, other):
        return isinstance(other, datetime.datetime)


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_order_billing_requests(
        stq_runner, mockserver, pgsql, load_json,
):
    @mockserver.json_handler(
        'taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def mock_mvp(request):
        mvp = 'MSKc' if request.query['tariff_zone'] == 'moscow' else 'BSKc'
        return {'oebs_mvp_id': mvp}

    @mockserver.json_handler('driver-tags/v1/drivers/match/profiles')
    def mock_tags(request):
        return {
            'drivers': [
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'tags': ['tag1', 'default_tag'],
                },
                {'dbid': 'dbid1', 'uuid': 'uuid1', 'tags': ['tag2']},
            ],
        }

    @mockserver.json_handler(
        'unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def mock_profiles(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid0_uuid0',
                    'data': {'unique_driver_id': 'udid0'},
                },
                {
                    'park_driver_profile_id': 'dbid1_uuid1',
                    'data': {'unique_driver_id': 'udid1'},
                },
            ],
        }

    @mockserver.json_handler('fleet-parks/v1/parks/list')
    def mock_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'dbid0',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'rus',
                    'name': 'park_name',
                    'org_name': 'org_name',
                    'geodata': {'lat': 12, 'lon': 34, 'zoom': 0},
                    'provider_config': {'clid': '123', 'type': 'production'},
                },
                {
                    'id': 'dbid1',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'rus',
                    'name': 'park_name',
                    'org_name': 'org_name',
                    'geodata': {'lat': 12, 'lon': 34, 'zoom': 0},
                    'provider_config': {
                        'clid': 'clid333',
                        'type': 'production',
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def mock_billing_client_id_retrieve(request):
        clid = request.query['park_id']
        client_id = 'billing_client_id_1' if clid == '123' else 'client2'
        return mockserver.make_response(
            json={'billing_client_id': client_id}, status=200,
        )

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def mock_billing_orders(request):
        assert request.json == load_json('orders_response.json')
        return {
            'orders': [
                {
                    'topic': (
                        'shuttle/order_id/2fef68c9-25d0-4174-9dd0-bdd1b3730775'
                    ),
                    'external_ref': '1',
                    'doc_id': 123,
                },
                {
                    'topic': (
                        'shuttle/order_id/427a330d-2506-464a-accf-346b31e288b9'
                    ),
                    'external_ref': '1',
                    'doc_id': 456,
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        response = []
        for dbid_uuid in request.json['id_in_set']:
            response.append(
                {
                    'data': {
                        'license': {'pd_id': dbid_uuid + '_license'},
                        'uuid': dbid_uuid.split('_')[1],
                    },
                    'park_driver_profile_id': dbid_uuid,
                },
            )
        return {'profiles': response}

    await stq_runner.shuttle_send_driver_billing_data.call(
        task_id='2_123321', kwargs={'request_ids': [1, 2]},
    )

    assert mock_mvp.times_called == 2
    assert mock_tags.times_called == 1
    assert mock_profiles.times_called == 1
    assert mock_parks_list.times_called == 1
    assert mock_billing_client_id_retrieve.times_called == 2
    assert mock_billing_orders.times_called == 1
    assert mock_driver_profiles.times_called == 1

    rows = select_named(
        'SELECT * FROM state.order_billing_requests ' 'ORDER BY request_id ',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 2
    assert rows == [
        {
            'request_id': 1,
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'doc_id': 123,
            'finished_at': AnyDateTime(),
            'timezone': 'Europe/Moscow',
            'nearest_zone': 'moscow',
            'state': 'finished',
        },
        {
            'request_id': 2,
            'booking_id': '427a330d-2506-464a-accf-346b31e288b9',
            'doc_id': 456,
            'finished_at': AnyDateTime(),
            'timezone': 'Europe/Moscow',
            'nearest_zone': 'bishkek',
            'state': 'finished',
        },
    ]
