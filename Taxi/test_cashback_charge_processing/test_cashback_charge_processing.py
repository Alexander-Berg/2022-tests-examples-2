# pylint: disable=too-many-lines
import datetime
import enum
import operator
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import aiohttp
import pytest

from taxi.stq import async_worker_ng

from cashback import const
from cashback.generated.stq3 import pytest_plugin as stq_plugin
from cashback.generated.stq3 import stq_context
from cashback.stq import cashback_charge_processing

PUSH_EDA_TPL = (
    '+{{value}} {form} на вашем Плюсе. Это кэшбек за заказ в Еде. Спасибо!'
)
PUSH_LAVKA_TPL = (
    '+{{value}} {form} на вашем Плюсе. Это кэшбек за заказ в Лавке. Спасибо!'
)

TRANSLATIONS = dict(
    client_messages={
        'personal_wallet.push_notification.cashback_from_eda': {
            'ru': [
                PUSH_EDA_TPL.format(form='балл'),
                PUSH_EDA_TPL.format(form='балла'),
                PUSH_EDA_TPL.format(form='баллов'),
                PUSH_EDA_TPL.format(form='баллов'),
            ],
        },
        'personal_wallet.push_notification.cashback_from_lavka': {
            'ru': [
                PUSH_LAVKA_TPL.format(form='балл'),
                PUSH_LAVKA_TPL.format(form='балла'),
                PUSH_LAVKA_TPL.format(form='баллов'),
                PUSH_LAVKA_TPL.format(form='баллов'),
            ],
        },
    },
)

CASHBACK_UPDATE_EXPERIMENT = dict(
    name=const.EXPERIMENT_PUSH_ON_CASHBACK_UPDATE,
    value={
        'eats': {
            'enabled': True,
            'tanker_key': 'cashback_from_eda',
            'origins': ['taxi'],
        },
        'grocery': {'enabled': True, 'tanker_key': 'cashback_from_lavka'},
    },
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'billing_service': 'card',
                },
            },
            'restaurants': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'restaurants',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                    'billing_service': 'food_payment',
                    'notify': [
                        {
                            'delivery_settings': {
                                'stq': {'queue': 'restaurants_callback'},
                            },
                            'delivery_type': 'stq',
                            'enabled': True,
                        },
                        {
                            'delivery_settings': {
                                'stq': {
                                    'queue': 'restaurants_callback_disabled',
                                },
                            },
                            'delivery_type': 'stq',
                            'enabled': False,
                        },
                    ],
                },
            },
            'eats': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'payments_eda',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                },
            },
            'grocery': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'eda',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'payments_eda',
                    'payment_methods_blacklist': ['personal_wallet', 'corp'],
                },
            },
        },
    ),
]


@pytest.fixture(name='mock_experiments')
def _mock_experiments(mockserver):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        if request.json['consumer'] == 'stq/cashback_charge_processing':

            res = []
            for arg in request.json['args']:
                if arg['name'] == 'yandex_uid' and arg['type'] == 'string':
                    if arg['value'] == 'yandex_uid_1':
                        res.append(CASHBACK_UPDATE_EXPERIMENT)

            return {'items': res}
        if request.json['consumer'] == 'user-wallet/create':
            return {
                'items': [
                    {
                        'name': 'user_wallet_create_via_plus_wallet',
                        'value': {},
                    },
                ],
            }

        return {'items': []}

    return _handler


@pytest.fixture(name='mock_ucommunications')
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _handler(request):
        return {}

    return _handler


class MyTestCase(NamedTuple):
    service: str = 'yataxi'
    user_info_origin: str = 'taxi'
    user_id: str = 'user_id_1'
    wallet_id: str = 'w/wallet_id'
    invoice_cashback: dict = {}
    invoice_status: str = 'init'
    events: List = []

    expected_cashback_update: Optional[dict] = None
    expected_payload: dict = {}
    expected_billing_service: Optional[str] = 'card'
    should_create_wallet: bool = False
    should_reschedule: bool = False
    push_text: Optional[str] = None

    def make_invoice_update(self) -> dict:
        rewarded = [
            {'amount': amount, 'source': source}
            for source, amount in self.invoice_cashback.items()
        ]

        return {
            'cashback': {
                'status': self.invoice_status,
                'version': 2,
                'rewarded': rewarded,
                'transactions': [],
                'commit_version': 1,
                'operations': [
                    {
                        'created': '2021-08-01T10:00:13+03:00',
                        'operation_id': 'cbba29c8fb0944f58525f7f0b329c274',
                        'yandex_uid': 'yandex_uid_1',
                        'user_ip': '2a02:6b8:b010:50a3::3',
                        'wallet_account': self.wallet_id,
                        'reward': rewarded,
                        'billing_service': 'card',
                        'extra_payload': {
                            'has_plus': True,
                            'base_amount': '979',
                        },
                        'status': 'done',
                    },
                ],
            },
            'external_user_info': {
                'user_id': self.user_id,
                'origin': self.user_info_origin,
            },
        }

    @property
    def expected_update_url(self) -> str:
        if self.service == 'restaurants':
            return '/transactions-eda/v2/cashback/update'
        return '/transactions/v2/cashback/update'


@pytest.mark.parametrize(
    'queue',
    ['cashback_charge_processing', 'cashback_charge_processing_non_critical'],
)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                events=[],
                should_reschedule=False,
                expected_cashback_update=None,
            ),
            id='no-events',
        ),
        pytest.param(
            MyTestCase(
                events=[
                    {'value': '100', 'source': 'user'},
                    {'value': '0', 'source': 'service'},
                ],
                expected_cashback_update={'service': '0', 'user': '100'},
                should_reschedule=True,
            ),
            id='event-source-user',
        ),
        pytest.param(
            MyTestCase(
                events=[
                    {
                        'value': '0',
                        'source': 'user',
                        'payload': {'payment_type': 'corp'},
                    },
                    {
                        'value': '100',
                        'source': 'service',
                        'payload': {'payment_type': 'corp'},
                    },
                ],
                expected_cashback_update={'service': '100', 'user': '0'},
                expected_payload={'payment_type': 'corp'},
                should_reschedule=True,
            ),
            id='event-source-service',
        ),
        pytest.param(
            MyTestCase(
                events=[
                    {'value': '100', 'source': 'user'},
                    {'value': '50', 'source': 'service'},
                ],
                expected_cashback_update={'service': '50', 'user': '100'},
                should_reschedule=True,
            ),
            id='event-source-both',
        ),
        pytest.param(
            MyTestCase(
                invoice_status='success',
                invoice_cashback={'user': '10', 'service': '10'},
                events=[
                    {'value': '100', 'source': 'user'},
                    {'value': '10', 'source': 'service'},
                ],
                expected_cashback_update={'service': '10', 'user': '100'},
                should_reschedule=True,
            ),
            id='yataxi-update-existing-cashback',
        ),
        pytest.param(
            MyTestCase(
                events=[{'value': '100', 'source': 'user'}],
                expected_cashback_update={'user': '100'},
                wallet_id='z5ffb8a68ec9f4f4fbf280dc6915357ff',
                should_create_wallet=True,
                should_reschedule=True,
            ),
            id='yataxi-create-wallet-before-update',
        ),
        pytest.param(
            MyTestCase(
                events=[
                    {'value': '100', 'source': 'user'},
                    {'value': '0', 'source': 'service'},
                ],
                invoice_cashback={'user': '100'},
                expected_cashback_update=None,
                should_reschedule=False,
            ),
            id='yataxi-event-matches-invoice',
        ),
        pytest.param(
            MyTestCase(
                events=[
                    {'value': '100', 'source': 'user'},
                    {'value': '10', 'source': 'service'},
                    {'value': '50', 'source': 'user'},
                    {'value': '0', 'source': 'service'},
                ],
                expected_cashback_update={'user': '50', 'service': '0'},
                should_reschedule=True,
            ),
            id='yataxi-multiple-events',
        ),
        pytest.param(
            MyTestCase(
                service='restaurants',
                events=[{'value': '500', 'source': 'service'}],
                expected_cashback_update={'service': '500'},
                should_reschedule=True,
                expected_billing_service='food_payment',
            ),
            id='restaurants-update',
        ),
        pytest.param(
            MyTestCase(
                service='eats',
                events=[{'value': '123', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '123'},
                push_text=(
                    '+123 балла на вашем Плюсе.'
                    ' Это кэшбек за заказ в Еде. Спасибо!'
                ),
            ),
            id='eats-update',
        ),
        pytest.param(
            MyTestCase(
                service='eats',
                events=[{'value': '123', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '123'},
                push_text=(
                    '+123,00 балла на вашем Плюсе.'
                    ' Это кэшбек за заказ в Еде. Спасибо!'
                ),
            ),
            marks=[
                pytest.mark.config(
                    CURRENCY_FORMATTING_RULES={
                        'RUB': {'__default__': 0, 'cashback': 2},
                    },
                ),
            ],
            id='eats-new-price-format',
        ),
        pytest.param(
            MyTestCase(
                service='grocery',
                events=[{'value': '321', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '321'},
                push_text=(
                    '+321 балл на вашем Плюсе.'
                    ' Это кэшбек за заказ в Лавке. Спасибо!'
                ),
            ),
            marks=[
                pytest.mark.config(
                    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 0}},
                ),
            ],
            id='grocery-update',
        ),
        pytest.param(
            MyTestCase(
                service='eats',
                events=[{'value': '1234', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '1234'},
                push_text=(
                    '+1234 балла на вашем Плюсе.'
                    ' Это кэшбек за заказ в Еде. Спасибо!'
                ),
            ),
            marks=[
                pytest.mark.config(
                    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 0}},
                ),
            ],
            id='eats-big-update',
        ),
        pytest.param(
            MyTestCase(
                service='eats',
                events=[{'value': '1234', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '1234'},
                user_info_origin='eats',
            ),
            id='eats-without-push',
        ),
        pytest.param(
            MyTestCase(
                service='restaurants',
                events=[
                    {
                        'value': '400',
                        'source': 'service',
                        'payload': {'has_plus': True, 'base_amount': '979'},
                    },
                ],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '400'},
            ),
            id='non-pushable-service-update-without-push',
        ),
        pytest.param(
            MyTestCase(
                service='eats',
                events=[{'value': '123', 'source': 'service'}],
                invoice_status='success',
                invoice_cashback={'user': '0', 'service': '123'},
                user_id='',
            ),
            marks=[
                pytest.mark.config(
                    CURRENCY_FORMATTING_RULES={
                        'RUB': {'__default__': 0, 'cashback': 2},
                    },
                ),
            ],
            id='eats-without-user-id',
        ),
    ],
)
@pytest.mark.translations(**TRANSLATIONS)
async def test_charge_processing_via_transactions(
        stq_runner: stq_plugin.Stq3Runner,
        stq,
        mockserver,
        mock_cashback,
        mock_plus_wallet,
        mock_plus_balances,
        balances_context,
        transactions_mock,
        mock_reschedule,
        mock_experiments,
        mock_ucommunications,
        case: MyTestCase,
        queue: str,
):
    @mock_cashback('/internal/events/mark-processed')
    async def _mock_events_processed(request, **kwargs):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/add/restaurants_callback')
    def _mock_notify_service(request):
        request_json = request.json
        request_json['kwargs']['last_operation']['reward'].sort(
            key=operator.itemgetter('amount', 'source'),
        )
        expected_task_id = 'order_id/cbba29c8fb0944f58525f7f0b329c274'
        assert request_json['task_id'] == expected_task_id

        expected_payload = {}
        for event in case.events:
            if event['source'] == 'service':
                expected_payload = event['payload']
                break
        assert request_json['kwargs'] == {
            'order_id': 'order_id',
            'last_operation': {
                'operation_id': 'cbba29c8fb0944f58525f7f0b329c274',
                'yandex_uid': 'yandex_uid_1',
                'reward': [
                    {'source': 'user', 'amount': '0'},
                    {'source': 'service', 'amount': '400'},
                ],
                'wallet_id': 'w/wallet_id',
                'user_ip': '2a02:6b8:b010:50a3::3',
                'extra_payload': expected_payload,
            },
        }

    transactions_mock.invoice_retrieve_v2.update(**case.make_invoice_update())
    balances_context.wallets = [
        {'wallet_id': case.wallet_id, 'currency': 'RUB'},
    ]

    @mock_cashback('/internal/events')
    async def _mock_events(request, **kwargs):
        assert request.query['service'] == case.service
        return {
            'events': [
                {
                    'event_id': 'event_id',
                    'external_ref': 'order_id',
                    'currency': 'RUB',
                    'value': '30',
                    'type': 'invoice',
                    'source': 'user',
                    'yandex_uid': 'yandex_uid_1',
                    'service': case.service,
                    'payload': {},
                    **event,
                }
                for event in case.events
            ],
        }

    @mockserver.json_handler(case.expected_update_url)
    async def _mock_cashback_update(request):
        expected_wallet_id = case.wallet_id
        if case.should_create_wallet:
            expected_wallet_id = 'newly_created_wallet'

        request_reward = {
            reward['source']: reward['amount']
            for reward in request.json['reward']
        }
        expected_reward = {**case.expected_cashback_update}

        assert request_reward == expected_reward
        assert request.json['invoice_id'] == 'order_id'
        assert request.json['operation_id'] == 'event_id'
        assert request.json['version'] == 2
        assert request.json['yandex_uid'] == 'yandex_uid_1'
        assert request.json['user_ip'] == '2a02:6b8:b010:50a3::3'
        assert request.json['wallet_account'] == expected_wallet_id
        assert request.json['billing_service'] == case.expected_billing_service
        assert request.json['extra_payload'] == case.expected_payload

        return {}

    @mock_plus_wallet('/v1/create')
    def _mock_create_wallet(request):
        assert request.json == {
            'yandex_uid': 'yandex_uid_1',
            'currency': 'RUB',
            'user_ip': '2a02:6b8:b010:50a3::3',
        }
        return {'wallet_id': 'newly_created_wallet'}

    queue_mock = mock_reschedule(queue)

    await getattr(stq_runner, queue).call(
        task_id='order_id',
        args=('order_id',),
        kwargs=dict(service=case.service),
    )

    if case.expected_cashback_update is not None:
        assert _mock_cashback_update.has_calls

    if not case.expected_cashback_update and case.service == 'restaurants':
        assert _mock_notify_service.times_called == 1

    assert queue_mock.has_calls == case.should_reschedule

    if not case.should_reschedule and case.events:
        assert _mock_events_processed.has_calls
    else:
        assert not _mock_events_processed.has_calls

    if case.push_text:
        assert mock_ucommunications.has_calls
        call_request = mock_ucommunications.next_call()['request'].json
        assert case.push_text == call_request['data']['payload']['msg']
    else:
        assert not mock_ucommunications.has_calls


@pytest.mark.parametrize(
    'queue',
    ['cashback_charge_processing', 'cashback_charge_processing_non_critical'],
)
async def test_charge_processing_invoice_in_progress(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        transactions_mock,
        mock_cashback,
        mock_cashback_events,
        mock_reschedule,
        queue,
):
    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'commit_version': 4,
                'status': 'in-progress',
                'version': 3,
                'rewarded': [{'amount': '17', 'source': 'service'}],
                'transactions': [],
                'operations': [],
            },
        },
    )

    mock_cashback_events()
    queue_mock = mock_reschedule(queue)

    await getattr(stq_runner, queue).call(
        task_id='order_id', args=('order_id',), kwargs=dict(service='yataxi'),
    )

    assert queue_mock.has_calls


class InvoiceFailedOutcome(enum.Enum):
    fail_events = 'fail_events'
    reschedule = 'reschedule'
    retry_update = 'retry_update'


class InvoiceFailedTestCase(NamedTuple):

    failed_operations: List[str]
    expected_outcome: InvoiceFailedOutcome
    expected_new_operation_id: Optional[str] = None

    last_operation_created_at: datetime.datetime = datetime.datetime(
        2021, 8, 1, 10, 0, 13, tzinfo=datetime.timezone.utc,
    )
    cashback_events: List[Dict[str, str]] = [
        {'event_id': 'event_id_1', 'source': 'user', 'value': '100'},
        {'event_id': 'event_id_2', 'source': 'service', 'value': '200'},
    ]

    def setup_invoice_retrieve_mock(self, transactions_mock):

        operations = [
            self._make_failed_operation(operation_id=operation_id)
            for operation_id in self.failed_operations
        ]
        # Replace the last operation with one with the specified created_at
        operations[-1] = self._make_failed_operation(
            operation_id=self.failed_operations[-1],
            created_at=self.last_operation_created_at,
        )

        transactions_mock.invoice_retrieve_v2.update(
            **{
                'cashback': {
                    'commit_version': 4,
                    'status': 'failed',
                    'version': 2,
                    'rewarded': [],
                    'transactions': [],
                    'operations': operations,
                },
            },
        )

    @property
    def should_increment_retries_metric(self) -> bool:
        if self.expected_new_operation_id is None:
            return False
        # pylint doesn't understand that expected_new_operation_id
        # is either an str or None
        # pylint: disable=unsupported-membership-test
        return 'retry' in self.expected_new_operation_id

    @property
    def expected_retry_metric(self) -> dict:
        expected_value = 1 if self.should_increment_retries_metric else 0
        return {
            'value': expected_value,
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'cashback.charge_processing.operation_retries',
            },
            'timestamp': None,
        }

    def setup_cashback_update_mock(self, mockserver):
        @mockserver.json_handler('/transactions-eda/v2/cashback/update')
        @mockserver.json_handler('/transactions/v2/cashback/update')
        async def _mock_cashback_update(request):
            assert self.expected_outcome is InvoiceFailedOutcome.retry_update

            assert request.json['invoice_id'] == 'order_id'
            new_operation_id = request.json['operation_id']
            assert new_operation_id == self.expected_new_operation_id

            return {}

        return _mock_cashback_update

    def setup_events_mark_mock(self, mock_cashback):
        @mock_cashback('/internal/events/mark-processed')
        async def _mock_mark_events(request):
            assert self.expected_outcome is InvoiceFailedOutcome.fail_events

            assert request.json['status'] == 'failed'
            expected_event_ids = [
                event['event_id'] for event in self.cashback_events
            ]
            assert request.json['event_ids'] == expected_event_ids
            return {}

        return _mock_mark_events

    def setup_events_retrieve_mock(self, mock_cashback, service):
        @mock_cashback('/internal/events')
        async def _mock_events(request, **kwargs):
            assert request.query['service'] == service
            return {
                'events': [
                    {
                        'external_ref': 'order_id',
                        'currency': 'RUB',
                        'type': 'invoice',
                        'yandex_uid': 'yandex_uid_1',
                        'service': service,
                        'payload': {},
                        **event,
                    }
                    for event in self.cashback_events
                ],
            }

        return _mock_events

    @staticmethod
    def _make_failed_operation(
            operation_id,
            created_at: datetime.datetime = datetime.datetime(
                2021, 8, 1, 10, 0, 13, tzinfo=datetime.timezone.utc,
            ),
    ) -> dict:
        return {
            'created': created_at.isoformat(),
            'operation_id': operation_id,
            'yandex_uid': 'yandex_uid_from_op',
            'user_ip': '2a02:6b8:b010:50a3::3',
            'wallet_account': 'w/b11ac0a3-94a1-5bd3-9a6f-9b4c73d0263a',
            'reward': [
                {'amount': '90.0000', 'source': 'service'},
                {'amount': '109.0000', 'source': 'user'},
            ],
            'billing_service': 'card',
            'extra_payload': {'has_plus': True, 'base_amount': '979'},
            'status': 'failed',
        }


@pytest.mark.parametrize('service', ['yataxi', 'restaurants'])
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            InvoiceFailedTestCase(
                failed_operations=['failed_op_id'],
                expected_outcome=InvoiceFailedOutcome.fail_events,
            ),
            marks=[
                pytest.mark.config(
                    CASHBACK_OPERATION_RETRY_POLICY={
                        'max_operations': 1,
                        'min_delay': '1s',
                        'max_delay': '2d',
                    },
                ),
            ],
            id='no-retries-left',
        ),
        pytest.param(
            InvoiceFailedTestCase(
                failed_operations=['event_id_2'],
                expected_outcome=InvoiceFailedOutcome.retry_update,
                expected_new_operation_id='event_id_2/retry/1',
            ),
            marks=[
                pytest.mark.config(
                    CASHBACK_OPERATION_RETRY_POLICY={
                        'max_operations': 3,
                        'min_delay': '1s',
                        'max_delay': '2d',
                    },
                ),
            ],
            id='retry-update',
        ),
        pytest.param(
            InvoiceFailedTestCase(
                failed_operations=[
                    'event_id_0',
                    'event_id_0/retry/1',
                    'event_id_0/retry/2',
                    'event_id_2',
                    'event_id_2/retry/1',
                    'event_id_2/retry/2',
                    'event_id_2/retry/3',
                ],
                expected_outcome=InvoiceFailedOutcome.retry_update,
                expected_new_operation_id='event_id_2/retry/4',
            ),
            marks=[
                pytest.mark.config(
                    CASHBACK_OPERATION_RETRY_POLICY={
                        'max_operations': 10,
                        'min_delay': '1s',
                        'max_delay': '2d',
                    },
                ),
            ],
            id='retry-update-one-more-time',
        ),
        pytest.param(
            InvoiceFailedTestCase(
                failed_operations=[
                    'failed_op_id',
                    'failed_op_id/retry/1',
                    'failed_op_id/retry/2',
                ],
                cashback_events=[
                    {
                        'event_id': 'event_id_3',
                        'source': 'user',
                        'value': '100',
                    },
                    {
                        'event_id': 'event_id_4',
                        'source': 'service',
                        'value': '200',
                    },
                ],
                expected_outcome=InvoiceFailedOutcome.retry_update,
                expected_new_operation_id='event_id_4',
            ),
            id='new-event-after-retry',
            marks=[
                pytest.mark.config(
                    CASHBACK_OPERATION_RETRY_POLICY={
                        'max_operations': 10,
                        'min_delay': '1s',
                        'max_delay': '2d',
                    },
                ),
            ],
        ),
        pytest.param(
            InvoiceFailedTestCase(
                failed_operations=[
                    'failed_op_id',
                    *[f'failed_op_id/retry/{retry}' for retry in range(1, 99)],
                ],
                expected_outcome=InvoiceFailedOutcome.reschedule,
                last_operation_created_at=datetime.datetime(
                    2021, 8, 1, 10, 0, 13, tzinfo=datetime.timezone.utc,
                ),
            ),
            marks=[
                # two seconds after the last operation was created
                pytest.mark.now('2021-08-01T10:00:15+00:00'),
                pytest.mark.config(
                    CASHBACK_OPERATION_RETRY_POLICY={
                        'max_operations': 100,
                        'min_delay': '1s',
                        'max_delay': '2d',
                    },
                ),
            ],
            id='too-early-to-retry',
        ),
    ],
)
async def test_charge_processing_invoice_failed(
        stq3_context: stq_context.Context,
        transactions_mock,
        mock_cashback,
        mockserver,
        mock_reschedule,
        mock_plus_balances,
        get_single_stat_by_label_values,
        service,
        case: InvoiceFailedTestCase,
):
    case.setup_invoice_retrieve_mock(transactions_mock)
    cashback_update_mock = case.setup_cashback_update_mock(mockserver)
    case.setup_events_retrieve_mock(mock_cashback, service)
    events_mock = case.setup_events_mark_mock(mock_cashback)

    reschedule_mock = mock_reschedule(
        'cashback_charge_processing', f'order_id/{service}',
    )

    await cashback_charge_processing.task_critical(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=f'order_id/{service}',
            exec_tries=0,
            reschedule_counter=0,
            queue='cashback_charge_processing',
        ),
        order_id='order_id',
        service=service,
    )

    metric = get_single_stat_by_label_values(
        stq3_context,
        {'sensor': 'cashback.charge_processing.operation_retries'},
    )
    assert metric == case.expected_retry_metric

    if case.expected_outcome is InvoiceFailedOutcome.fail_events:
        assert events_mock.has_calls
        return

    if case.expected_outcome is InvoiceFailedOutcome.retry_update:
        assert cashback_update_mock.has_calls
        return

    if case.expected_outcome is InvoiceFailedOutcome.reschedule:
        reschedule_call = reschedule_mock.next_call()
        eta = reschedule_call['request'].json['eta']
        eta = datetime.datetime.strptime(eta, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
            tzinfo=datetime.timezone.utc,
        )
        delay = eta - case.last_operation_created_at

        # Delay is randomized so we have to do a range check.
        # Two days is max_delay from CASHBACK_OPERATION_RETRY_POLICY
        assert delay / 1.5 <= datetime.timedelta(days=2) <= delay / 0.5

        return


async def test_charge_processing_no_user_ip(
        stq3_context: stq_context.Context,
        transactions_mock,
        mock_cashback,
        mockserver,
):
    transactions_mock.invoice_retrieve_v2.update(user_ip=None)

    @mockserver.json_handler('/transactions/v2/cashback/update')
    async def _mock_cashback_update(request):
        assert False, 'cashback/update should not be called'

    @mock_cashback('/internal/events')
    async def _mock_events(request, **kwargs):
        return {
            'events': [
                {
                    'event_id': 'event_id',
                    'external_ref': 'order_id',
                    'currency': 'RUB',
                    'value': '30',
                    'type': 'invoice',
                    'source': 'user',
                    'yandex_uid': 'yandex_uid_1',
                    'service': 'yataxi',
                    'payload': {},
                },
            ],
        }

    with pytest.raises(ValueError):
        await cashback_charge_processing.task_critical(
            context=stq3_context,
            task_info=async_worker_ng.TaskInfo(
                id=f'order_id/yataxi',
                exec_tries=0,
                reschedule_counter=0,
                queue='cashback_charge_processing',
            ),
            order_id='order_id',
            service='yataxi',
        )


@pytest.mark.parametrize(
    'queue',
    ['cashback_charge_processing', 'cashback_charge_processing_non_critical'],
)
async def test_transactions_ratelimiter(
        stq_runner: stq_plugin.Stq3Runner,
        mockserver,
        transactions_mock,
        mock_cashback,
        mock_billing_wallet,
        mock_plus_balances,
        mock_cashback_events,
        mock_reschedule,
        queue,
):
    transactions_mock.invoice_retrieve_v2.update(
        **{
            'cashback': {
                'commit_version': 12,
                'status': 'init',
                'version': 2,
                'rewarded': [],
                'transactions': [],
                'operations': [],
            },
            'external_user_info': {'user_id': 'user_id_1', 'origin': 'taxi'},
        },
    )

    @mockserver.json_handler('/transactions/v2/cashback/update')
    async def _mock_cashback_update(request):
        return aiohttp.web.json_response(status=429, data='Limit exceeded')

    queue_mock = mock_reschedule(queue)
    mock_cashback_events()

    await getattr(stq_runner, queue).call(
        task_id='order_id', args=('order_id',), kwargs=dict(service='yataxi'),
    )

    assert _mock_cashback_update.has_calls
    assert queue_mock.has_calls
