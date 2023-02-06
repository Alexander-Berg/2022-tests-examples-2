# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import yql_tasks.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['yql_tasks.generated.service.pytest_plugins']


class MockYqlRequestOperation:
    operation_id = 'test_op_id'
    share_url = 'test_share_url'

    def run(self, parameters=None):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    @staticmethod
    def get_results(*args, **kwargs):
        return MockYqlResults


class MockYqlTable:

    column_names: list = []

    def get_iterator(self):
        return []


class MockYqlResults:
    status = 'completed'
    is_success = True
    errors: list = []
    table = MockYqlTable

    def fetch_full_data(self):
        pass


class MockYqlRequestOperationError:
    operation_id = 'test_op_id'
    share_url = 'test_share_url'

    def run(self, parameters=None):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    @staticmethod
    def get_results(*args, **kwargs):
        return MockYqlResultsError


class MockYqlResultsError:
    status = 'error'
    is_success = False
    errors: list = ['asdfasdfsf']


@pytest.fixture
def simple_secdist(simple_secdist):
    # в нужные секции дописываем свои значения
    simple_secdist['settings_override'].update(
        {
            'YQL_TOKEN': 'test_token',
            'INFRANAIM_APIKEYS': {
                'park_rejected_lead': 'token_park_rejected_lead',
            },
        },
    )
    return simple_secdist


@pytest.fixture
def mock_yt_call(patch):
    def _wrapper(response):
        @patch('yql_tasks.internal.yql_tasks_manager.make_query_by_file')
        def _handler(*args, **kwargs):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_update_hiring_details(mock_driver_profiles):
    @mock_driver_profiles('/v1/contractor/hiring-details')
    def _handler(request):
        return {}

    return _handler
