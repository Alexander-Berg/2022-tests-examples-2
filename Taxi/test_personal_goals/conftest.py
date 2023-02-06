# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
# pylint: disable=wrong-import-order
import json

import pytest

from generated.models import taxi_tariffs as tariffs

import personal_goals.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from personal_goals.modules.cashback import plus_transactions
from personal_goals.utils import postgres
from personal_goals.utils import time_storage

pytest_plugins = ['personal_goals.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_context_vars():
    time_storage.init_time_storage('TESTS')


@pytest.fixture
def make_default_order(load_json):
    def _make_order(order):
        default_order = load_json('default_order.json')
        return {**default_order, **order}

    return _make_order


@pytest.fixture
def make_default_goal(load_json):
    def _make_goal(goal):
        default_goal = load_json('default_goal.json')
        goal_dict = {**default_goal, **goal}
        for dump_field in ['conditions', 'bonus']:
            goal_dict[dump_field] = json.dumps(goal_dict[dump_field])
        return goal_dict

    return _make_goal


class BaseFacade:
    p_key = 'id'
    table_name: str

    def __init__(self, web_context):
        self.pgaas = web_context.pg

    async def by_query(self, query, *query_args):
        return await postgres.fetch(self.pgaas, query, *query_args)

    async def all(self):
        query = 'SELECT * FROM personal_goals.{}'.format(self.table_name)
        return await self.by_query(query)

    async def by_ids(self, ids):
        query = (
            """
        SELECT * FROM personal_goals.{}
        WHERE {} = ANY($1)
        """.format(
                self.table_name, self.p_key,
            )
        )
        return await self.by_query(query, ids)

    async def by_user_goal(self, user_goal):
        query = (
            """
        SELECT * FROM personal_goals.{}
        WHERE user_goal = $1
        """.format(
                self.table_name,
            )
        )
        return await self.by_query(query, user_goal)


class GoalEventsFacade(BaseFacade):
    table_name = 'user_goal_events'


class UserGoalsFacade(BaseFacade):
    table_name = 'user_goals'


class GoalsFacade(BaseFacade):
    table_name = 'goals'


class SelectionFacade(BaseFacade):
    table_name = 'selections'
    p_key = 'selection_id'


class NotificationsFacade(BaseFacade):
    table_name = 'user_notifications'

    async def by_status(self, status):
        query = (
            """
        SELECT * FROM personal_goals.{}
        WHERE status = $1
        """.format(
                self.table_name,
            )
        )
        return await self.by_query(query, status)


class ImportTasksFacade(BaseFacade):
    table_name = 'import_tasks'
    p_key = 'import_task_id'


@pytest.fixture
def pg_goals(web_context):
    class Ctx:
        def __init__(self, web_context):
            self.goals = GoalsFacade(web_context)
            self.user_goals = UserGoalsFacade(web_context)
            self.notifications = NotificationsFacade(web_context)
            self.goal_events = GoalEventsFacade(web_context)
            self.selections = SelectionFacade(web_context)
            self.import_tasks = ImportTasksFacade(web_context)

    return Ctx(web_context)


@pytest.fixture
def taxi_tariffs(mock_taxi_tariffs, load_json):
    class Context:
        tariff_settings_resp: dict

        def __init__(self):
            self.tariff_settings_resp = load_json(
                'default_get_tariff_settings.json',
            )

    context = Context()

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _mock_get_tariff_settings(*args, **kwargs):
        return context.tariff_settings_resp

    return context


@pytest.fixture
def default_tariff_settings(load_json):
    obj = load_json('default_get_tariff_settings.json')
    return tariffs.TariffSettingsItem.deserialize(
        obj['zones'][0]['tariff_settings'],
    )


@pytest.fixture
def plus_transactions_fixt(mockserver, mock_plus_transactions, load_json):
    class Context:
        ext_ref_id: str = 'ext_ref_id_1'
        yandex_uid: str = 'yandex_uid_1'
        currency: str = 'RUB'

        cashback_status: str = 'init'
        order_id: str = 'order_id_1'
        has_plus: str = 'true'
        update_cashback_amount: str = '100'
        update_cashback_exception: Exception = None

        @staticmethod
        def make_error_response(code):
            return mockserver.make_response(
                status=code, json={'code': str(code), 'message': ''},
            )

    context = Context()

    @mock_plus_transactions('/plus-transactions/v1/cashback/status')
    def _mock_cashback_status(request):
        assert request.query['ext_ref_id'] == context.ext_ref_id
        assert request.query['service_id'] == 'personal-goals-taxi'
        assert request.query['consumer'] == 'personal-goals'
        return {
            'status': context.cashback_status,
            'version': 1,
            'amount': '0',
            'operations': [],
        }

    @mock_plus_transactions('/plus-transactions/v1/cashback/update')
    def _mock_cashback_update(request):
        assert request.json['ext_ref_id'] == context.ext_ref_id
        assert request.json['service_id'] == 'personal-goals-taxi'
        assert request.json['consumer'] == 'personal-goals'
        assert request.json['yandex_uid'] == context.yandex_uid
        assert request.json['currency'] == context.currency
        assert request.json['user_ip'] == ''
        assert request.json['version'] == 1

        amount_by_source = request.json['amount_by_source']['service']
        assert amount_by_source['amount'] == context.update_cashback_amount

        payload = amount_by_source['payload']
        assert payload == {
            # Common payload
            'cashback_service': 'yataxi',
            'cashback_type': 'transaction',
            'service_id': '124',
            'issuer': 'taxi',
            'campaign_name': 'personal_goals_taxi',
            'ticket': 'NEWSERVICE-000',
            'has_plus': str(context.has_plus).lower(),
            'product_id': 'personal_goals_cashback_bonus',
            # Taxi order payload
            'order_id': context.order_id,
            'base_amount': '356.0',
            'alias_id': 'alias_id',
            'oebs_mvp_id': 'MSKc',
            'tariff_class': 'econom',
            'currency': 'RUB',
            'country': 'RU',
        }

        exception = context.update_cashback_exception
        if exception == plus_transactions.UpdateCashbackRaceCondition:
            return context.make_error_response(409)
        return mockserver.make_response(status=200, json={})

    return context


@pytest.fixture
def mock_reschedule(mockserver):
    def _make_mock(queue):
        @mockserver.json_handler('/stq-agent/queues/api/reschedule')
        def _handler(request):
            assert request.json['queue_name'] == queue
            assert request.json['task_id'] == '100_RUB_cashback'
            return {}

        return _handler

    return _make_mock
