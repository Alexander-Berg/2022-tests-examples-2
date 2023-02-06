import getpass
import json

import pytest

from cargo_newflow import consts
from cargo_newflow.clients import (
    cargo_claims,
    cargo_orders_internal,
    cargo_waybill,
    ordercore,
    taximeter_x_service,
    telegram,
)
from cargo_newflow import library
from cargo_newflow import reporter as reporter_lib
from cargo_newflow import utils


def pytest_addoption(parser):
    group = parser.getgroup('telegram')
    group.addoption(
        '--telegram',
        action='store_true',
        help='nice: turn failures into opportunities',
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':  # execution result
        setattr(item, 'rep_' + report.when, report)


@pytest.fixture(scope='session')
def net_address():
    return utils.guess_address()


@pytest.fixture(scope='session')
def username():
    return getpass.getuser()


@pytest.fixture(scope='session')
def test_data(request):
    return request.param


@pytest.fixture(scope='session')
def cargo_client(net_address, username, test_data):
    cargo_client = cargo_claims.CargoClaimsClient(
        corp_client_id=test_data['corp_client_id'],
        yandex_uid=test_data['yandex_uid'],
        user=username,
        net_address=net_address,
    )
    return cargo_client


@pytest.fixture(scope='session')
def waybill_client(username, net_address):
    waybill_client = cargo_waybill.CargoWaybillClient(
        user=username, net_address=net_address,
    )
    return waybill_client


@pytest.fixture(scope='session')
def journals_client(cargo_client):
    journals = library.Journals(claims_client=cargo_client)
    return journals


@pytest.fixture(scope='session')
def order_core_client(net_address):
    order_core_client = ordercore.OrderCoreClient(net_address=net_address)
    return order_core_client


@pytest.fixture(scope='session')
def taximeter_xservice_client(net_address):
    taximeter_xservice_client = taximeter_x_service.TaximeterXServiceClient(
        net_address=net_address,
    )
    return taximeter_xservice_client


@pytest.fixture(scope='session')
def cargo_order_client(net_address):
    cargo_order_client = cargo_orders_internal.CargoOrdersInternalClient(
        net_address=net_address,
    )
    return cargo_order_client


@pytest.fixture(autouse=True)
def make_custom_report(request):
    yield
    if request.config.getoption('--telegram'):
        newflow_config_path = utils.get_project_root() / consts.NEWFLOW_CONFIG
        conf = utils.load_config(newflow_config_path)

        telegram_client = telegram.TelegramClient(
            bot_token=conf.get('default', 'bot-token'),
            chat_id=conf.get('default', 'chat-id'),
        )
        telegram_reporter = reporter_lib.TelegramReporter(
            client=telegram_client,
            enable_alerts=True,
            report_file_path=conf.get('default', 'report-file'),
        )
        request_sections = dict(request.node.rep_call.sections)
        report = {}
        additional_info = request_sections.get(
            'Captured Claim link call', None,
        )
        if additional_info:
            additional_info = json.loads(additional_info)
            report.update(additional_info)

        report['result'] = telegram_client.make_bold(
            request.node.rep_call.outcome,
        )
        if request.node.rep_call.passed:
            report = '\n'.join(
                '{}: {}'.format(k, v) for k, v in report.items()
            )
            telegram_reporter.write_log(report)

        elif request.node.rep_call.failed:
            order_logs = request_sections.get('Captured Order logs call', None)
            if order_logs:
                order_logs = json.loads(order_logs)
                report.update(order_logs)
            report['error'] = telegram_client.make_code_style(
                request.node.rep_call.longrepr.reprcrash.message,
            )
            report = '\n\n'.join(
                '{}: {}'.format(k, v) for k, v in report.items()
            )
            telegram_reporter.write_log(report)
            telegram_reporter.call_on_duty()

        telegram_reporter.send_report(parse_mode='HTML')
