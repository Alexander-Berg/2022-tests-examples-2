# pylint: disable=redefined-outer-name
import pytest

import taxi_admin_personal.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_admin_personal.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def mock_countries(patch):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    async def _get_all_countries(*args, **kwargs):
        return [
            {
                '_id': 'rus',
                'national_access_code': '8',
                'phone_code': '7',
                'phone_max_length': 11,
                'phone_min_length': 11,
            },
        ]

    return _get_all_countries


@pytest.fixture  # noqa: F405
def mock_pd_phones(mockserver):
    class MockContext:
        def __init__(self):
            self.bulk_find_count = 0
            self.bulk_retrieve_count = 0
            self.phones_bulk_find = None
            self.phones_bulk_retrieve = None

    context = MockContext()

    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    # pylint: disable=unused-variable
    async def _phones_bulk_find(request):
        context.bulk_find_count += 1
        return {
            'items': list(
                map(
                    lambda x: {'id': 'id_' + x['value'], 'value': x['value']},
                    request.json['items'],
                ),
            ),
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    # pylint: disable=unused-variable
    async def _phones_bulk_retrieve(request):
        context.bulk_retrieve_count += 1
        return {
            'items': list(
                map(
                    lambda x: {
                        'id': x['id'],
                        'value': x['id'].replace('id_', ''),
                    },
                    request.json['items'],
                ),
            ),
        }

    context.phones_bulk_find = _phones_bulk_find
    context.phones_bulk_retrieve = _phones_bulk_retrieve

    return context


@pytest.fixture  # noqa: F405
def mock_deptrans_ids(mockserver):
    class MockContext:
        pass

    context = MockContext()

    @mockserver.json_handler(
        '/deptrans-driver-status/internal/v1/profiles/bulk-retrieve',
    )
    async def _bulk_retrieve(request):
        return {
            'items': [
                {
                    'park_id': 'test_id_2',
                    'driver_id': 'f977c37e2653e61186a6001e671f718e',
                    'status': 'approved',
                    'deptrans_pd_id': 'id_123',
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/deptrans_ids/bulk_retrieve')
    async def _personal_deptrans_ids(request):
        return {
            'items': list(
                map(
                    lambda x: {
                        'id': x['id'],
                        'value': x['id'].replace('id_', ''),
                    },
                    request.json['items'],
                ),
            ),
        }

    setattr(context, 'bulk_retrieve', _bulk_retrieve)
    setattr(context, 'personal_deptrans_ids', _personal_deptrans_ids)

    return context
