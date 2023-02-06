# pylint: disable=redefined-outer-name
import pytest

import gpdb_manager_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['gpdb_manager_api.generated.service.pytest_plugins']


@pytest.fixture
def gpdb_manager_api_auth_mock(mockserver):
    @mockserver.handler('/gpdb-manager-api/auth_request', prefix=True)
    def _get_username(request):
        return mockserver.make_response(
            status=200, headers={'X-Webauth-Login': 'unittest_user'},
        )


# @pytest.fixture
# def load_json(load_json):
#     def _load_py_json(filename, *args, **kwargs):
#         static_dir = os.path.join(
#             os.path.dirname(os.path.abspath(__file__)), 'static',
#         )
#         return load_json(os.path.join(static_dir, filename), *args, **kwargs)
#
#     return _load_py_json
