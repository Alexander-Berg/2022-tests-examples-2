import enum
import json
import os
from typing import Optional
import warnings

import pytest

from taxi_testsuite.plugins import api_coverage
from . import userver_client


_API_COVERAGE_TEST_NAME = 'test_api_coverage'


class NotificationMode(enum.Enum):
    SILENT = 'silent'
    WARNING = 'warning'
    ERROR = 'error'


def pytest_addoption(parser) -> None:
    group = parser.getgroup('services')
    group.addoption(
        '--api-coverage-notification-mode',
        dest='api_coverage_notification_mode',
        type=NotificationMode,
        default=NotificationMode.ERROR,
        choices=[
            NotificationMode.SILENT,
            NotificationMode.WARNING,
            NotificationMode.ERROR,
        ],
        help=(
            'Notification mode for API Coverage check. '
            'Might be: - "silent", "warning", "error"'
        ),
    )


@pytest.fixture(scope='session')
def api_coverage_report():
    return api_coverage.CoverageReport()


@pytest.fixture(autouse=True)
def patched_requests(
        monkeypatch, api_coverage_report, is_api_coverage_enabled,
):
    old_request = userver_client.AiohttpClient._request  # noqa

    async def wrapped_request(self, http_method, path, *args, **kwargs):
        response = await old_request(self, http_method, path, *args, **kwargs)
        api_coverage_report.update_usage_stat(
            path, http_method, response.status, response.content_type,
        )
        return response

    if is_api_coverage_enabled:
        monkeypatch.setattr(
            userver_client.AiohttpClient, '_request', wrapped_request,
        )


@pytest.fixture(scope='function')
def collect_coverage_report(
        api_coverage_report,
        get_source_path,
        get_service_name,
        testsuite_output_dir,
        schema_endpoints,
        api_coverage_non_decreasing,
        pytestconfig,
        request,
):
    session_items = request.session.items
    if request.node.nodeid != session_items[-1].nodeid:
        return

    service_name = get_service_name
    report = api_coverage_report.generate_report(
        service_endpoints=schema_endpoints,
    )
    report_path: str = testsuite_output_dir / 'report.json'
    report.save_to_file(report_path)
    current_service_api_coverage_ratio = report.coverage_ratio
    request.config.cache.set(
        'service_api_coverage_ratio', current_service_api_coverage_ratio,
    )
    request.config.cache.set('api_coverage_report_path', str(report_path))

    if is_teamcity():
        aggregated_coverage_report_path = get_source_path(
            'aggregated_report',
        ).resolve()
        update_aggregated_api_coverage_report(
            aggregated_coverage_report_path=aggregated_coverage_report_path,
            service_name=service_name,
            coverage_ratio=report.coverage_ratio,
        )

        if api_coverage_non_decreasing:
            previous_ratio = get_current_service_api_coverage_ratio(
                get_source_path('previous_report').resolve(), service_name,
            )
            if previous_ratio is None:
                return
            if current_service_api_coverage_ratio < previous_ratio:
                pytest.fail(
                    msg=(
                        'Current API Coverage ratio is less '
                        'than previous historical value: {0} < {1}'
                    ).format(
                        current_service_api_coverage_ratio, previous_ratio,
                    ),
                    pytrace=False,
                )

    mode: NotificationMode = pytestconfig.option.api_coverage_notification_mode

    if api_coverage_non_decreasing:
        report.coverage_validate(strict=False)
        return

    if mode == NotificationMode.WARNING:
        report.coverage_validate(strict=False)
    elif mode == NotificationMode.ERROR:
        report.coverage_validate(strict=True)
    elif mode == NotificationMode.SILENT:
        return
    else:
        raise Exception(f'Unknown NotificationMode "{mode}"')


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    api_coverage_report_path = config.cache.get(
        'api_coverage_report_path', None,
    )
    if not api_coverage_report_path:
        return
    if exitstatus > 1:
        return
    terminalreporter.ensure_newline()
    terminalreporter.section(
        'HTTP API Coverage', sep='-', blue=True, bold=True,
    )
    terminalreporter.line(
        f'Path to API coverage report: {api_coverage_report_path}',
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_collection_modifyitems(items):
    yield
    if len(items) == 0:
        return

    api_coverage_indices = [
        i
        for i in range(len(items))
        if items[i].name == _API_COVERAGE_TEST_NAME
    ]

    if not api_coverage_indices:
        return

    modified_items = []

    for i in range(len(items)):
        if i != api_coverage_indices[-1]:
            modified_items.append(items[i])
    modified_items.append(items[api_coverage_indices[-1]])
    items[:] = modified_items


def is_teamcity() -> bool:
    if os.getenv('IS_TEAMCITY'):
        return True
    return False


def update_aggregated_api_coverage_report(
        aggregated_coverage_report_path: str,
        service_name: str,
        coverage_ratio: float,
) -> None:
    with open(aggregated_coverage_report_path, 'a') as aggregated_report:
        aggregated_report.write(f'{service_name} - {coverage_ratio}\n')


def get_current_service_api_coverage_ratio(
        previous_report: str, service_name: str,
) -> Optional[float]:
    ratio: Optional[float] = None
    try:
        with open(previous_report) as report:
            content = json.load(report)
            for service in content['services']:
                if service['service_name'] == service_name:
                    ratio = float(service['coverage_ratio'])

        if ratio is None:
            warnings.warn(
                f'API Coverage ratio for service "{service_name}" was not found',
            )
    except FileNotFoundError as exc:
        warnings.warn(
            f'Cannot read file with API Coverage data for services: {exc}',
        )
        return None
    return ratio
