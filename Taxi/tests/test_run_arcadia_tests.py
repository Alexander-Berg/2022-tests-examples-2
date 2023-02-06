import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Sequence

import run_arcadia_tests
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    service_yaml: Dict[str, Any]
    services_to_test: Sequence[str]
    ya_calls: Sequence[List[str]]


DEFAULT_YA_ARGS = [
    'ya',
    'make',
    '-A',
    '--build',
    'release',
    '--teamcity',
    '--output',
    '/output',
    '--junit',
    '/output/test-results/tier0-tests.xml',
]


PARAMS = [
    Params(
        pytest_id='single_tier0_service',
        services_to_test=['arcadia-userver-test'],
        service_yaml={'ya-make': {'enabled': True}},
        ya_calls=[[*DEFAULT_YA_ARGS, 'services/arcadia-userver-test']],
    ),
    Params(
        pytest_id='single_tier1_service',
        services_to_test=['arcadia-userver-test'],
        service_yaml={
            'ya-make': {'owners': ['rumkex', 'g:taxi-automatization']},
        },
        ya_calls=[],
    ),
    Params(
        pytest_id='multiple_services_test_one',
        services_to_test=['arcadia-userver-test', 'driver-authorizer'],
        service_yaml={'ya-make': {'enabled': True}},
        ya_calls=[[*DEFAULT_YA_ARGS, 'services/arcadia-userver-test']],
    ),
    Params(
        pytest_id='multiple_services_test_zero',
        services_to_test=['arcadia-userver-test', 'driver-authorizer'],
        service_yaml={
            'ya-make': {'owners': ['rumkex', 'g:taxi-automatization']},
        },
        ya_calls=[],
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_arcadia_test_runner(
        params: Params,
        commands_mock,
        monkeypatch,
        tmpdir,
        load,
        load_json,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
        patch_requests,
):
    work_dir = arcadia.init_uservices(
        tmpdir,
        main_service='arcadia-userver-test',
        changelog_content=None,
        service_yaml=params.service_yaml,
    )
    monkeypatch.chdir(work_dir)

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        return 0

    run_arcadia_tests.main(
        (
            *params.services_to_test,
            '--output-dir',
            '/foo/../output',
            '--test-reports-dir',
            '/bar/../output/test-results',
        ),
    )

    assert [call['args'] for call in ya_mock.calls] == params.ya_calls
