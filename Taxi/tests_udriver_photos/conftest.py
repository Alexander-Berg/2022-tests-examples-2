# pylint: disable=redefined-outer-name
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from udriver_photos_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_unique_drivers(mockserver):
    def set_unique_id(unique_driver_id, return_code=200):
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
        )
        def _unique_driver_id_handler(request):
            if return_code != 200:
                return mockserver.make_response(
                    'expected fail', status=return_code,
                )
            data = {
                'park_driver_profile_id': request.json['profile_id_in_set'][0],
            }
            if unique_driver_id is None:
                return {'uniques': [{**data}]}
            return {
                'uniques': [
                    {'data': {'unique_driver_id': unique_driver_id}, **data},
                ],
            }

    return set_unique_id


@pytest.fixture
def mock_order_core(mockserver):
    def set_performer(
            park_id, driver_profile_id, tariff='econom', return_code=200,
    ):
        @mockserver.json_handler('/order-core/v1/tc/order-fields')
        def _get_order(request):
            assert set(request.json['fields']) == {
                'order.nz',
                'order.performer.db_id',
                'order.performer.uuid',
                'order.performer.tariff.class',
            }
            order_id = request.json['order_id']
            if return_code == 404:
                return mockserver.make_response(
                    '{"code":"404","message":"Order not found"}', status=404,
                )
            if return_code == 500:
                return mockserver.make_response(
                    'internal server error', json={}, status=return_code,
                )
            if return_code == 200:
                return {
                    'fields': {
                        '_id': order_id,
                        'order': {
                            'nz': 'moscow',
                            'performer': {
                                'tariff': {'class': tariff},
                                'uuid': driver_profile_id,
                                'db_id': park_id,
                            },
                        },
                    },
                    'order_id': order_id,
                    'replica': 'secondary',
                    'version': 'DAAAAAAABgAMAAQABgAAAMhRRnlxAQAA',
                }

            raise RuntimeError(f'unexpected return_code: {return_code}')

    return set_performer


@pytest.fixture
def mock_candidates(mockserver):
    def _mock(
            park_id,
            driver_profile_id,
            tariffs,
            return_code=200,
            is_network_error=False,
    ):
        @mockserver.json_handler('/candidates/profiles')
        def _position_handler(request):
            assert request.method == 'POST'
            assert request.json['driver_ids'] == [
                {'dbid': park_id, 'uuid': driver_profile_id},
            ]
            assert request.json['data_keys'] == ['classes']

            if return_code != 200:
                return mockserver.make_response(
                    'expected fail', status=return_code,
                )
            if is_network_error:
                raise mockserver.NetworkError()
            return {
                'drivers': [
                    {
                        'dbid': park_id,
                        'uuid': driver_profile_id,
                        'position': [33.0, 55.0],
                        'classes': tariffs,
                    },
                ],
            }

    return _mock
