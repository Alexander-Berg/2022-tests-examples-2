# pylint: disable=duplicate-code
import datetime as dt
import logging
import os
from typing import Mapping

import pytest
import pytz

import taxi
from taxi.pytest_plugins import service

from taxi_billing_subventions import config as subventions_config
from taxi_billing_subventions import main
from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import py_json_converters

TVM_TICKET = 'good_ticket'


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'subventions_config: subventions config',
    )


@pytest.fixture
def request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing_subventions')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def stq_client_patched(patch):
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def stq_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        return

    return stq_client_put


@pytest.fixture(name='billing_subventions_app')
def billing_subventions_app_fixture(loop, simple_secdist, mongodb_init):
    simple_secdist['billing_subventions'] = {}
    return main.init_billing_subventions_app()


@pytest.fixture
def billing_subventions_client(
        aiohttp_client, billing_subventions_app, loop, territories_mock,
):
    return loop.run_until_complete(aiohttp_client(billing_subventions_app))


@pytest.fixture
def load_py_json_dir(load_py_json):
    def _load_py_json_dir(dir_name, *input_data):
        if not input_data:
            raise RuntimeError('pass some fixture')
        elif len(input_data) == 1:
            return load_py_json(os.path.join(dir_name, input_data[0]))
        else:
            return [
                load_py_json(os.path.join(dir_name, a_data))
                for a_data in input_data
            ]

    return _load_py_json_dir


@pytest.fixture(name='load_py_json')
def load_py_json_fixture(load_py_json):
    def _load_py_json(filename):
        return load_py_json(filename, py_json_converters.CONVERTERS)

    return _load_py_json


@pytest.fixture
def patched_syslog_handler(monkeypatch):
    logs = []

    class StubLogHandler(logging.Handler):
        def __init__(self, *args, **kwargs):
            super().__init__()

        def emit(self, record):
            if getattr(record, '_link', None):
                to_save = {
                    'level': record.levelname,
                    '_link': record._link,  # pylint: disable=protected-access
                    'msg': record.getMessage(),
                    'exc_info': bool(record.exc_info),
                }
                logs.append(to_save)

    monkeypatch.setattr('taxi.logs.log.SysLogHandler', StubLogHandler)

    return logs


@pytest.fixture(name='subventions_config', autouse=True)
def subventions_config_fixture(request, monkeypatch):
    marker = request.node.get_closest_marker('subventions_config')
    if marker:
        config_patch = marker.kwargs.items()

        for config_key, value in config_patch:
            monkeypatch.setattr(
                subventions_config.Config, config_key, value, raising=False,
            )


@pytest.yield_fixture
def decimal_prec_8():
    import decimal
    with decimal.localcontext() as ctx:
        ctx.prec = 8
        yield


@pytest.fixture(name='patched_discovery')
def enable_mockserver_for_services(patch):
    real_find_service = taxi.discovery.find_service
    mocks = {
        'billing_docs': '$mockserver/billing-docs',
        'billing_subventions': '$mockserver/billing-subventions',
        'parks-replica': '$mockserver/parks-replica',
    }

    @patch(
        'taxi_billing_subventions.process_doc._context.discovery.find_service',
    )
    def _find_service(service_name):
        srv = real_find_service(service_name)
        if srv.name in mocks:
            srv = taxi.discovery.Service(srv.name, mocks[service_name])
        return srv


@pytest.fixture(name='patched_secdist')
def _patch_secdist_loading(patch):
    secdist = {}

    @patch(
        'taxi_billing_subventions.process_doc._context.secdist.load_secdist',
    )
    def _load_secdist():
        return secdist

    @patch(
        'taxi_billing_subventions.process_doc._context.'
        'secdist.load_secdist_ro',
    )
    def _load_secdist_ro():
        return secdist


@pytest.fixture(name='zones_cache')
def make_zones_cache():
    class ZonesCache:
        def __init__(self):
            self.zones_by_name = {'moscow': ZonesCache.get_zone('moscow')}

        @staticmethod
        def get_zone(name) -> models.Zone:
            return models.Zone(
                name=name,
                city_id='Москва',
                tzinfo=pytz.timezone('Europe/Moscow'),
                currency='RUB',
                locale='ru',
                vat=models.Vat.make_naive(12000),
                country='RU',
            )

        @property
        def tzinfo_by_zone(self) -> Mapping[str, dt.tzinfo]:
            return {'moscow': dt.timezone.utc}

    return ZonesCache()


@pytest.yield_fixture
async def stq_process_doc_context(
        db, zones_cache, patched_discovery, patched_secdist,
):
    from taxi_billing_subventions.process_doc import _context
    context = _context.ContextData(db=db, zones_cache=zones_cache)
    yield context
    await context._session.close()  # pylint: disable=protected-access


@pytest.fixture
def mock_billing_docs(mockserver):
    def _mock_billing_docs(*existed_docs):
        docs = {int(doc['doc_id']): doc for doc in existed_docs}
        doc_id_gen = _id_generator(5000)

        class Mocker:
            created_docs = []
            finished_docs = []

            @mockserver.json_handler('/billing-docs/v1/docs/create')
            @staticmethod
            def create(request):
                Mocker.created_docs.append(request.json)
                doc = dict(request.json)
                doc['doc_id'] = next(doc_id_gen)
                doc.pop('journal_entries')
                return doc

            @mockserver.json_handler(
                '/billing-docs/v1/docs/is_ready_for_processing',
            )
            @staticmethod
            def is_ready_for_processing(request):
                return {'ready': True, 'doc': docs[request.json['doc_id']]}

            @mockserver.json_handler('/billing-docs/v1/docs/search')
            @staticmethod
            def docs_search(request):
                if 'doc_id' in request.json:
                    result = [docs[request.json['doc_id']]]
                if 'kind' in request.json:
                    result = [
                        doc
                        for doc in docs.values()
                        if doc['kind'] == request.json['kind']
                    ]
                return {'docs': result}

            @mockserver.json_handler('/billing-docs/v1/docs/finish_processing')
            @staticmethod
            def finish_processing(request):
                Mocker.finished_docs.append(request.json['doc_id'])
                return {}

            @mockserver.json_handler('/billing-docs/v1/docs/update')
            @staticmethod
            def update(request):
                return docs[request.json['doc_id']]

        return Mocker()

    return _mock_billing_docs


@pytest.fixture
def mock_billing_accounts(mockserver):
    def _mock_accounts():
        account_id_gen = _id_generator(1000)

        class Mocker:
            created_accounts = []

            @mockserver.json_handler('/billing-accounts/v1/entities/search')
            @staticmethod
            def v1_entities_search(request):
                return []

            @mockserver.json_handler('/billing-accounts/v1/entities/create')
            @staticmethod
            def v1_entities_create(request):
                return {}

            @mockserver.json_handler('/billing-accounts/v1/accounts/search')
            @staticmethod
            def v1_accounts_search(request):
                return []

            @mockserver.json_handler('/billing-accounts/v1/accounts/create')
            @staticmethod
            def v1_accounts_create(request):
                Mocker.created_accounts.append(request.json)
                account = request.json
                account['account_id'] = next(account_id_gen)
                return account

        return Mocker()

    return _mock_accounts


@pytest.fixture
def mock_billing_orders(mockserver):
    def _mock_orders():
        class Mocker:
            events = []

            @mockserver.json_handler('/billing-orders/v2/process/async')
            @staticmethod
            def v2_process_async(request):
                Mocker.events.append(request.json)
                return {'orders': []}

        return Mocker()

    return _mock_orders


def _id_generator(start=1, end=None):
    yield from range(start, end if end is not None else start + 1000)


@pytest.fixture
def mock_billing_subventions(mockserver):
    def _mock_subventions():
        class Mocker:
            scheduled_docs = []

            @mockserver.json_handler('/billing-subventions/v1/process_doc')
            @staticmethod
            def process_doc(request):
                Mocker.scheduled_docs.append(request.json)
                return {}

        return Mocker()

    return _mock_subventions


@pytest.fixture
def mock_antifraud(mockserver):
    def _make_mock(subventions_check_response_json):
        @mockserver.json_handler('/antifraud/v1/subventions/check')
        def v1_subventions_check(request):
            assert list(subventions_check_response_json.keys()) == ['items']
            return subventions_check_response_json

        return v1_subventions_check

    return _make_mock


@pytest.fixture
def mock_uantifraud(mockserver):
    def _make_mock(uantifraud_response):
        @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
        def v1_subvention_check_order(request):
            return uantifraud_response

        return v1_subvention_check_order

    return _make_mock


@pytest.fixture
def mock_subvention_communications(mockserver):
    class _Mock:
        @mockserver.json_handler(
            '/subvention-communications/v1/driver_fix/pay',
        )
        @staticmethod
        def v1_driver_fix_pay(request):
            return {}

        @mockserver.json_handler(
            '/subvention-communications/v1/driver_fix/block',
        )
        @staticmethod
        def v1_driver_fix_block(request):
            return {}

        @mockserver.json_handler('/subvention-communications/v1/rule/pay')
        @staticmethod
        def v1_rule_pay(request):
            return {}

        @mockserver.json_handler('/subvention-communications/v1/rule/fraud')
        @staticmethod
        def v1_rule_fraud(request):
            return {}

    yield _Mock()


@pytest.fixture(name='mock_parks_replica')
def make_mock_parks_replica(mockserver):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _wrapper(_):
        return {'billing_client_id': 'billing_client_id'}

    return _wrapper


@pytest.fixture(name='mock_billing_replication')
def make_mock_billing_replication(mockserver, load_json):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _wrapper(_):
        return load_json('replication_contracts.json')

    return _wrapper


@pytest.fixture(name='mock_billing_subventions_x')
def make_mock_billing_subventions_x(mockserver, load_json):
    def _make_mock(response_json):
        @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
        def _wrapper(request):
            return load_json(response_json)

        return _wrapper

    return _make_mock


service.install_service_local_fixtures(__name__)
