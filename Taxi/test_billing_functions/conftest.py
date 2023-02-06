# pylint: disable=redefined-outer-name
import collections
import copy
import datetime as dt
import functools
from typing import List
from typing import Union

import pytest

import billing_functions.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from test_billing_functions import py_json_hooks

pytest_plugins = ['billing_functions.generated.service.pytest_plugins']


@pytest.fixture
def billing_context(stq3_context):
    return stq3_context


@pytest.fixture
def mock_docs_component(stq3_context, monkeypatch):
    from billing.tests import mocks

    lag = stq3_context.config.BILLING_DOCS_REPLICATION_LAG_MS
    docs = mocks.TestDocs(replication_lag_ms=lag)
    monkeypatch.setattr(stq3_context, 'docs', docs)
    return docs


@pytest.fixture
def mock_billing_components(stq3_context, mock_docs_component, monkeypatch):
    from billing.tests import mocks

    class BillingComponents:
        def __init__(self, now: dt.datetime):
            self.docs = mock_docs_component
            self.accounts = mocks.TestAccounts()
            cfg = stq3_context.config
            journal_ttl = cfg.BILLING_OLD_JOURNAL_LIMIT_DAYS
            journal_lag = cfg.BILLING_ACCOUNTS_JOURNAL_REPLICATION_LAG_MS
            self.journal = mocks.TestJournal(
                self.accounts,
                now,
                max_entries_age_days=journal_ttl,
                replication_lag_ms=journal_lag,
            )
            self.entities = mocks.TestEntities()

    def _wrapper(now: dt.datetime) -> BillingComponents:
        components = BillingComponents(now)
        monkeypatch.setattr(stq3_context, 'accounts', components.accounts)
        monkeypatch.setattr(stq3_context, 'journal', components.journal)
        monkeypatch.setattr(stq3_context, 'entities', components.entities)
        return components

    return _wrapper


@pytest.fixture(name='mock_antifraud')
def make_mock_antifraud(mockserver):
    def _mock_antifraud(antifraud_responses):
        class Results:
            requests = []

        @mockserver.json_handler('/antifraud/v1/subventions/check')
        def _check(request):
            Results.requests.append(request.json)
            response = {'items': [antifraud_responses.pop(0)]}
            return response

        return Results()

    return _mock_antifraud


@pytest.fixture(name='mock_subvention_communications')
def make_mock_subvention_comms(mockserver):
    class Results:
        requests = []

    def _mock():
        results = Results()

        @mockserver.json_handler('/subvention-communications/v1/rule/pay')
        def _check(request):
            results.requests.append(request.json)

        return results

    return _mock


@pytest.fixture(name='mock_tlog')
def make_mock_tlog(mock_billing_tlog):
    class Mocker:
        journal_v1 = []
        journal_v2 = []

        @staticmethod
        def make_tlog_response_entries(request):
            entries = request['entries']
            entries_copy = copy.deepcopy(entries)
            for entry in entries_copy:
                entry['id'] = 1
                entry['transaction_time'] = '2019-07-17T12:00:00+03:00'
                entry['topic'] = entry.get('topic', 'topic')
                entry['partition'] = 'partition'
            return entries_copy

        @mock_billing_tlog('/v1/journal/append')
        @staticmethod
        def _v1_append(request):
            Mocker.journal_v1.append(request.json)
            return {'entries': Mocker.make_tlog_response_entries(request.json)}

        @mock_billing_tlog('/v2/journal/append')
        @staticmethod
        def _v2_append(request):
            Mocker.journal_v2.append(request.json)
            return {'entries': Mocker.make_tlog_response_entries(request.json)}

    return Mocker()


@pytest.fixture(name='mock_limits')
def make_mock_limits(mock_billing_limits):
    class Mocker:
        requests = []

        @mock_billing_limits('/v1/deposit')
        @staticmethod
        def _deposit(request):
            Mocker.requests.append(request.json)
            return {}

    return Mocker()


@pytest.fixture(name='mock_processing')
def make_processing(mock_processing):
    class Mocker:
        processing_v1 = []

        @mock_processing('/v1/pro/contractors_income/create-event')
        @staticmethod
        def _v1_contractors_income_append(request):
            Mocker.processing_v1.append(request.json)
            return {'event_id': 'f47b5d12fb2f40c684b4365f65684728'}

    return Mocker()


@pytest.fixture(name='mock_driver_work_modes')
def make_mock_driver_work_modes(mock_driver_work_modes, load_json, mockserver):
    def _mock_driver_work_modes(dwm_responses_json=None):
        responses = load_json(dwm_responses_json) if dwm_responses_json else {}

        class Mocker:
            requests = collections.defaultdict(list)

            @staticmethod
            @mockserver.handler('/driver-work-modes', prefix=True)
            def _v1_park_commission_rules_match(request):
                path = request.path
                service_prefix = '/driver-work-modes'
                if path.startswith(service_prefix):
                    path = path[len(service_prefix) :]
                if path in responses.keys():
                    Mocker.requests[path].append(request.json)
                    return mockserver.make_response(**(responses[path]))
                raise AssertionError(
                    f'Cannot get driver-work-modes response for path {path}',
                )

        return Mocker()

    return _mock_driver_work_modes


@pytest.fixture(name='mock_billing_commissions')
def make_mock_billing_commissions(mock_billing_commissions):
    def _mock_commissions(
            *, agreements=None, categories=None, rebate_agreement=None,
    ):
        class Results:
            rules_match_requests = []

        @mock_billing_commissions('/v1/rules/match')
        def _match_rules(request):
            Results.rules_match_requests.append(request.json)
            return {'agreements': agreements or []}

        @mock_billing_commissions('/v1/rebate/match')
        def _match_rebate_rule(request):
            Results.rules_match_requests.append(request.json)
            return {'agreement': rebate_agreement or {}}

        @mock_billing_commissions('/v1/categories/select')
        def _categories_select(request):
            return {'categories': categories or []}

        return Results()

    return _mock_commissions


@pytest.fixture(name='mock_billing_subventions_x')
def make_mock_billing_subventions_x(mock_billing_subventions_x):
    def _mock_bsx(
            v1_rules_match_responses: List[dict],
            v2_rules_match_responses: List[dict],
    ):
        @mock_billing_subventions_x('/v1/rules/match')
        def _v1_rules_match(request):
            _mock_bsx.v1_rules_match_requests.append(request.json)
            return v1_rules_match_responses.pop(0)

        @mock_billing_subventions_x('/v2/rules/match')
        def _v2_rules_match(request):
            _mock_bsx.v2_rules_match_requests.append(request.json)
            return v2_rules_match_responses.pop(0)

    _mock_bsx.v1_rules_match_requests = []
    _mock_bsx.v2_rules_match_requests = []

    return _mock_bsx


@pytest.fixture(name='mock_replication')
def make_mock_billing_replication(mock_billing_replication):
    def _mock_replication(contracts: list):
        @mock_billing_replication('/v1/active-contracts/')
        def _v1_active_contracts(request):
            return contracts

    return _mock_replication


@pytest.fixture(name='patched_stq_reschedule')
def make_patched_stq_reschedule(mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _patch_stq_agent_reschedule(request):
        return {}

    return _patch_stq_agent_reschedule


@pytest.fixture(name='patched_stq_queue')
def make_patched_stq_queue(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _patch_stq_agent_queue(request, queue_name):
        return {}

    def _pop_calls():
        result = []
        while _patch_stq_agent_queue.times_called:
            call = _patch_stq_agent_queue.next_call()['request'].json
            result.append(call)
        return result

    _patch_stq_agent_queue.pop_calls = _pop_calls

    return _patch_stq_agent_queue


@pytest.fixture(name='reschedulable_stq_runner')
def make_reschedulable_stq_runner(
        mocked_time, stq3_client, patched_stq_reschedule,
):
    async def _reschedulable_stq_runner(queue, doc_id):
        await queue.call(task_id='', args=(doc_id,))
        times_called = 0
        while patched_stq_reschedule.times_called:
            times_called += 1
            if times_called > 30:
                raise RuntimeError('Too many rescheduling')
            mocked_time.sleep(1)
            patched_stq_reschedule.next_call()
            await stq3_client.invalidate_caches()

            await queue.call(task_id='', args=(doc_id,))

    return _reschedulable_stq_runner


def pytest_configure(config):
    config.addinivalue_line('markers', 'json_obj_hook: json_obj_hook')


@pytest.fixture(name='load_common_py_json')
def make_load_common_py_json(load_py_json):
    hooks = py_json_hooks.HOOKS

    def _load_py_json(json_path, extra_hooks: dict = None):
        return load_py_json(json_path, {**hooks, **(extra_hooks or {})})

    return _load_py_json


@pytest.fixture(name='load_py_json')
def make_load_py_obj_json(request, load_common_py_json):
    mark = request.node.get_closest_marker('json_obj_hook')
    hooks = {}

    def _load_py_json(json_path, extra_hooks: dict = None):
        return load_common_py_json(json_path, {**hooks, **(extra_hooks or {})})

    hooks.update(**_make_obj_hooks_from_marker(mark, _load_py_json))
    hooks.update({'$load_py_json': _load_py_json})
    return _load_py_json


def _make_obj_hooks_from_marker(marker, load_py_json):
    obj_hooks = marker.kwargs if marker else {}

    def _class_obj_hook(cls, doc: Union[dict, list]):
        if isinstance(doc, list):
            return cls(*doc)
        if '@ref' in doc:
            ref = doc.pop('@ref')
            data = load_py_json(ref)
            data.update(doc)
            return cls(**data)
        return cls(**doc)

    return {
        f'${key}': functools.partial(_class_obj_hook, value)
        for key, value in obj_hooks.items()
    }
