import pytest

import store_api_coverage
from taxi_buildagent.clients import coverage_statistics
from tests.utils.examples import arcadia


API_COVERAGE_STORAGE_URL = (
    coverage_statistics.STATISTICS_URL + '/api/v1/coverage'
)
COMMIT_ID = '91ff05c64be03ce491620e8c95251d3d3df08caf'


@pytest.mark.parametrize(
    'branch,aggregated_report_content,expected_request',
    [
        pytest.param(
            'trunk',
            (
                'test-service-1 - 1.0\n'
                'test-service-2 - 0.5\n'
                'test-service-3 - 0.1'
            ),
            [
                {
                    'kwargs': {
                        'json': {
                            'services': [
                                {
                                    'commit_id': COMMIT_ID,
                                    'coverage_ratio': 1.0,
                                    'repository': 'uservices',
                                    'service_name': 'test-service-1',
                                },
                                {
                                    'commit_id': COMMIT_ID,
                                    'coverage_ratio': 0.5,
                                    'repository': 'uservices',
                                    'service_name': 'test-service-2',
                                },
                                {
                                    'commit_id': COMMIT_ID,
                                    'coverage_ratio': 0.1,
                                    'repository': 'uservices',
                                    'service_name': 'test-service-3',
                                },
                            ],
                        },
                        'params': None,
                        'timeout': 5.0,
                    },
                    'method': 'POST',
                    'url': API_COVERAGE_STORAGE_URL,
                },
            ],
            id='trunk',
        ),
        pytest.param(
            'users/olegsavinov/feature/EDAQA-1042',
            'test-service-1 - 1.0',
            [],
            id='different_branch',
        ),
    ],
)
def test_store_coverage(
        commands_mock,
        monkeypatch,
        patch_requests,
        tmpdir,
        branch,
        aggregated_report_content,
        expected_request,
):
    work_dir = arcadia.init_dummy(tmpdir)
    uservices_dir = work_dir / 'uservices'
    aggregated_report = uservices_dir / 'aggregated_report'

    uservices_dir.mkdir(exist_ok=True, parents=True)

    aggregated_report.write_text(aggregated_report_content)
    monkeypatch.chdir(work_dir)

    # pylint: disable=unused-variable
    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'log':
            return (
                """[
    {
        "commit": "91ff05c64be03ce491620e8c95251d3d3df08caf",
        "parents": ["d87515019c02a9106a8be4eadbe58cada43f78d1"],
        "author": "olegsavinov",
        "date": "2022-03-04T14:07:31+03:00",
        "message": "test",
        "branches": {
            "local": ["%s"],
            "remote": ["%s"],
            "head": true
        }
    }
]"""
                % (branch, branch)
            )
        if command == 'info':
            return (
                """{
    "summary": "test",
    "date": "2022-03-04T14:07:31+03:00",
    "hash": "91ff05c64be03ce491620e8c95251d3d3df08caf",
    "remote_head": "91ff05c64be03ce491620e8c95251d3d3df08caf",
    "branch": "%s",
    "remote": "%s",
    "author": "olegsavinov"
}"""
                % (branch, branch)
            )
        return ''

    @patch_requests(API_COVERAGE_STORAGE_URL)
    def api_coverage_storage_mock(method, url, **kwargs):
        return patch_requests.response(
            status_code=201, json={'stored_records': 3},
        )

    store_api_coverage.main(['--path-to-repo', 'uservices'])
    assert api_coverage_storage_mock.calls == expected_request
