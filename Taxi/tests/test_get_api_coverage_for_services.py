import json
import pathlib

import get_api_coverage_for_services
from taxi_buildagent.clients import coverage_statistics


API_COVERAGE_STORAGE_URL = (
    coverage_statistics.STATISTICS_URL + '/api/v1/coverage'
)
COMMIT_ID = '91ff05c64be03ce491620e8c95251d3d3df08caf'
RESPONSE = {
    'services': [
        {
            'service_name': 'test-service-1',
            'coverage_ratio': 1.0,
            'commit_id': COMMIT_ID,
            'repository': 'uservices',
        },
        {
            'service_name': 'test-service-2',
            'coverage_ratio': 0.5,
            'commit_id': COMMIT_ID,
            'repository': 'uservices',
        },
    ],
}


def test_get_coverage(commands_mock, monkeypatch, patch_requests, tmpdir):
    root_dir = pathlib.Path(tmpdir)
    root_dir.joinpath('uservices').mkdir(parents=True)

    previous_report = root_dir / 'uservices' / 'previous_report'
    monkeypatch.chdir(root_dir)

    @patch_requests(API_COVERAGE_STORAGE_URL)
    def api_coverage_storage_mock(method, url, **kwargs):
        return patch_requests.response(status_code=200, json=RESPONSE)

    get_api_coverage_for_services.main(
        ['--path-to-coverage-report', 'uservices/previous_report'],
    )
    assert api_coverage_storage_mock.calls == [
        {
            'kwargs': {'json': None, 'params': None, 'timeout': 5.0},
            'method': 'GET',
            'url': API_COVERAGE_STORAGE_URL,
        },
    ]
    with previous_report.open() as previous_report:
        content = json.load(previous_report)
        assert content == RESPONSE
