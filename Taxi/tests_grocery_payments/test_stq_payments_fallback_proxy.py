import uuid

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from .plugins import configs


ITEMS = [models.Item(item_id='item-id-1', price='10', quantity='2')]

FALLBACK_PROCESSING = 'sberbank_rbs_h2h_ru'

COUNTRY = models.Country.Russia

INVOICE_VERSION = 123

PAYMENT_TYPE = 'card'
TERMINAL_ID = '64285345'
FALLBACK_NAME = 'common_fallback_name'
PAYTURE_TO_SBER_FALLBACK_NAME = 'payture_to_sber_name'

FAIL = consts.OPERATION_FAILED
DONE = consts.OPERATION_DONE

ERROR_REASON_CODE = 'some_error_123'

STATUS_TO_ERROR = {DONE: None, FAIL: ERROR_REASON_CODE}

STATUS_TO_TRANSACTION_STATUS = {DONE: 'hold_success', FAIL: 'hold_fail'}

SENSOR_FALLBACK_METRICS = 'grocery_payments_fallback_proxy_metrics'

PAYTURE_TO_SBER_LABEL = (
    f'{consts.PAYTURE_TERMINAL_ID} '
    f'({consts.PAYTURE_NAME}) - '
    f'{consts.SBERBANK_TERMINAL_ID} '
    f'({consts.SBERBANK_NAME})'
)

PAYTURE_TO_UNKNOWN_LABEL = (
    f'{consts.PAYTURE_TERMINAL_ID} '
    f'({consts.PAYTURE_NAME}) - '
    f'{consts.TERMINAL_ID}'
)


class MockHelper:
    def __init__(
            self,
            mock_transactions,
            grocery_payments_configs,
            check_transactions_callback,
    ):
        self.mock_transactions = mock_transactions
        self.grocery_payments_configs = grocery_payments_configs
        self.check_transactions_callback = check_transactions_callback

        self.transactions = []
        self.operations = []

        self.config_fallbacks = []

    def add_attempt(
            self,
            operation_id,
            status,
            terminal_id=TERMINAL_ID,
            fallback_name=None,
            payment_type=PAYMENT_TYPE,
            external_payment_id=None,
    ):
        transaction_payload = None
        if fallback_name is not None:
            transaction_payload = {
                'payment_fallback': {'fallback_name': fallback_name},
            }

        if external_payment_id is None:
            external_payment_id = 'transaction-' + operation_id

        self.transactions.append(
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type=payment_type,
                terminal_id=terminal_id,
                transaction_payload=transaction_payload,
                error_reason_code=STATUS_TO_ERROR[status],
                status=STATUS_TO_TRANSACTION_STATUS[status],
                external_payment_id=external_payment_id,
            ),
        )

        self.operations.append(
            helpers.make_operation(
                id=operation_id,
                sum_to_pay=[
                    {
                        'items': models.to_transaction_items(ITEMS),
                        'payment_type': payment_type,
                    },
                ],
                status=status,
            ),
        )

    def mock_retrieve(self):
        self.mock_transactions.retrieve.mock_response(
            transactions=self.transactions,
            operations=self.operations,
            operation_info={
                'originator': 'processing',
                'priority': 1,
                'version': INVOICE_VERSION,
            },
        )

    def check_update(self, operation_id, processing_cc, fallback_name):
        check_dict = dict(
            operation_id=operation_id,
            id=consts.ORDER_ID,
            pass_params={
                'terminal_route_data': {
                    'preferred_processing_cc': processing_cc,
                },
            },
            items_by_payment_type=[
                {
                    'items': models.to_operation_items(ITEMS),
                    'payment_type': PAYMENT_TYPE,
                },
            ],
            transaction_payload={
                'payment_fallback': {'fallback_name': fallback_name},
            },
            version=INVOICE_VERSION,
        )

        self.mock_transactions.update.check(**check_dict)

    def add_fallback(
            self,
            fallback_name=None,
            terminal_id=None,
            processing_cc=FALLBACK_PROCESSING,
            country=None,
            retries_count=1,
    ):
        if terminal_id is None:
            terminal_id = str(uuid.uuid4())
        if fallback_name is None:
            fallback_name = str(uuid.uuid4())

        country_iso3 = None
        if country is not None:
            country_iso3 = country.country_iso3

        self.config_fallbacks.append(
            {
                'processing_cc': processing_cc,
                'name': fallback_name,
                'retries_count': retries_count,
                'terminal_id': terminal_id,
            },
        )

        self.grocery_payments_configs.add_payments_fallbacks(
            fallbacks=self.config_fallbacks, country_iso3=country_iso3,
        )

    def set_update_error_code(self, error_code):
        self.mock_transactions.update.status_code = error_code

    def check_task_proxy(self, must_proxy, **kwargs):
        if must_proxy:
            self.check_transactions_callback(times_called=1, **kwargs)
            if self.mock_transactions.update.is_ok:
                assert self.mock_transactions.update.times_called == 0
        else:
            self.check_transactions_callback(times_called=0, **kwargs)
            assert self.mock_transactions.update.times_called == 1

    def check_do_nothing(self):
        assert self.mock_transactions.update.times_called == 0
        self.check_transactions_callback(times_called=0)

    def get_callback_transaction(self, index: int):
        transaction = self.transactions[index]
        return {
            'external_payment_id': transaction['external_payment_id'],
            'payment_type': transaction['payment_type'],
            'status': transaction['status'],
        }


@pytest.fixture(name='mock_helper')
def _mock_helper_fixture(
        transactions, grocery_payments_configs, check_transactions_callback,
):
    helper = MockHelper(
        transactions, grocery_payments_configs, check_transactions_callback,
    )
    return helper


# Тест проверяет базовый флоу - создание второй попытки платежа, если
# есть подходящий фолбэк в конфиге.
async def test_create_second_operation(
        grocery_orders, run_payments_fallback_proxy_stq, mock_helper,
):
    operation_id = 'create:1'
    terminal_id = '2809'

    # Создаем обычную попытку на оплату (самую первую). Делаем вид,
    # что она зафейлилась.
    mock_helper.add_attempt(operation_id, FAIL, terminal_id=terminal_id)
    mock_helper.mock_retrieve()

    operation_id_retry = operation_id + ':attempt:1'

    # Создаем фолбэк
    fallback_name = 'some_name'
    mock_helper.add_fallback(
        processing_cc=FALLBACK_PROCESSING, fallback_name=fallback_name,
    )

    # Проверяем, что мы создали еще одну операцию в процессинг из фолбэка.
    mock_helper.check_update(
        operation_id=operation_id_retry,
        processing_cc=FALLBACK_PROCESSING,
        fallback_name=fallback_name,
    )

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=False)


# Тест проверяет, что если операция была успешная, то происходит проксирование
# события дальше. А если не успешная, то срабатывает фолбэк.
@pytest.mark.parametrize('status, must_proxy', [(DONE, True), (FAIL, False)])
async def test_proxy_if_success_operation(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        status,
        must_proxy,
):
    operation_id = 'create:1'

    mock_helper.add_attempt(operation_id, status=status)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=status,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Проверяем, что если из конфига ничего не пришло, то сработает прокси таски.
@pytest.mark.parametrize(
    'country, must_proxy', [(COUNTRY, False), (models.Country.Israel, True)],
)
async def test_proxy_if_config_not_matched(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        country,
        must_proxy,
):
    operation_id = 'create:1'

    mock_helper.add_attempt(operation_id, status=FAIL)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback(country=country)

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


async def test_configs_kwargs(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        experiments3,
):
    operations = ['create:1', 'create:1:attempt:1', 'create:1:attempt:2']
    used_terminals = ['111', '222', '333']

    for operation_id, terminal_id in zip(operations, used_terminals):
        mock_helper.add_attempt(
            operation_id, status=FAIL, terminal_id=terminal_id,
        )
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    exp3_recorder = experiments3.record_match_tries(
        'grocery_payments_fallback',
    )

    originator = models.InvoiceOriginator.tips
    await run_payments_fallback_proxy_stq(
        originator=originator,
        operation_id=operations[-1],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['consumer'] == 'grocery-payments/payments-fallback'
    assert exp3_kwargs['country_iso3'] == COUNTRY.country_iso3
    assert exp3_kwargs['payment_method_type'] == PAYMENT_TYPE
    assert exp3_kwargs['personal_phone_id'] == headers.PERSONAL_PHONE_ID
    assert exp3_kwargs['region_id'] == consts.REGION_ID
    assert exp3_kwargs['terminal_id'] == used_terminals[-1]
    assert exp3_kwargs['yandex_uid'] == headers.YANDEX_UID
    assert exp3_kwargs['error_reason_code'] == ERROR_REASON_CODE
    assert exp3_kwargs['originator'] == originator.request_name


USED_FALLBACK_NAME = 'used_fallback_name'
# Тест проверяет, что мы не используем один и тот же фолбэк дважды, если
# retries_count для фолбэка равен 1.
@pytest.mark.parametrize(
    'config_fallback_name, must_proxy',
    [('new_fallback', False), (USED_FALLBACK_NAME, True)],
)
async def test_ignore_used_fallback(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        config_fallback_name,
        must_proxy,
):
    operations = ['create:1', 'create:1:attempt:1', 'create:1:attempt:2']
    used_fallback_names = ['111', USED_FALLBACK_NAME, '333']

    for operation_id, fallback_name in zip(operations, used_fallback_names):
        mock_helper.add_attempt(
            operation_id, status=FAIL, fallback_name=fallback_name,
        )
    mock_helper.mock_retrieve()

    mock_helper.add_fallback(fallback_name=config_fallback_name)

    await run_payments_fallback_proxy_stq(
        operation_id=operations[-1],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет, что мы применяем фолбэк еще раз, если это позволяет сделать
# retries_count фолбэка. Если все попытки исчерпаны, то проксируем событие.
@pytest.mark.parametrize(
    'retries_count, must_proxy', [(1, True), (999, False)],
)
async def test_fallback_retries_count(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        retries_count,
        must_proxy,
):
    fallback_name = str(uuid.uuid4())

    first_operation = 'create:1'
    fallback_operations = [
        f'{first_operation}:attempt:1',
        f'{first_operation}:attempt:2',
    ]

    mock_helper.add_attempt('create:1', status=FAIL)
    for operation_id in fallback_operations:
        mock_helper.add_attempt(
            operation_id, status=FAIL, fallback_name=fallback_name,
        )

    mock_helper.mock_retrieve()

    mock_helper.add_fallback(
        fallback_name=fallback_name, retries_count=retries_count,
    )

    await run_payments_fallback_proxy_stq(
        operation_id=fallback_operations[-1],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет, что если произошла ошибка при создании повторной операции,
# то будет проксирование таски дальше.
@pytest.mark.parametrize(
    'error_code, must_proxy',
    [(200, False), (404, True), (409, True), (500, False)],
)
async def test_proxy_if_cannot_update(
        grocery_orders,
        transactions,
        run_payments_fallback_proxy_stq,
        mock_helper,
        error_code,
        must_proxy,
):
    operation_id = 'create:1'

    mock_helper.add_attempt(operation_id, status=FAIL)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    mock_helper.set_update_error_code(error_code)

    expect_fail = False
    if error_code == 500:
        expect_fail = True

    await run_payments_fallback_proxy_stq(
        expect_fail=expect_fail,
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет, что если пришел колбэк о старой операции, то он будет
# спроксирован дальше, потому что кто-то уже создал новую операцию и нет
# смысла пытаться повторить старую.
@pytest.mark.parametrize('make_not_actual', [True, False])
async def test_proxy_if_not_actual_operation(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        make_not_actual,
):
    operation_id_1 = 'create:1'
    operation_id_2 = 'update:2'

    mock_helper.add_attempt(operation_id_1, status=FAIL)
    if make_not_actual:
        mock_helper.add_attempt(operation_id_2, status=DONE)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id_1,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=make_not_actual)


# Тест проверяет, что если пришел колбэк не про завершение операции, то мы
# проксируем такие колбэки дальше.
@pytest.mark.parametrize(
    'notification_type, must_proxy',
    [(consts.OPERATION_FINISH, False), (consts.TRANSACTION_CLEAR, True)],
)
async def test_proxy_if_not_operation_finish_event(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        notification_type,
        must_proxy,
):
    operation_id_1 = 'create:1'

    mock_helper.add_attempt(operation_id_1, status=FAIL)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id_1,
        notification_type=notification_type,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет, что если пришел старый колбэк про повторную операцию, то мы
# с ним ничего не делаем. Такое может случится, если произошел таймаут
# при создании операции и к нам приходит одновременно два колбэка: ретрай
# старой операции + результат новой. Проксировать это не надо, потому что
# старая может быть не успешной, а новая успешной и мы зафейлим весь заказ.
@pytest.mark.parametrize('op_idx, do_nothing', [(1, True), (2, False)])
async def test_do_nothing_if_outdated_retry(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        op_idx,
        do_nothing,
):
    operations = ['create:1', 'create:1:attempt:1', 'create:1:attempt:2']

    for operation_id in operations:
        mock_helper.add_attempt(operation_id, status=FAIL)
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    await run_payments_fallback_proxy_stq(
        operation_id=operations[op_idx],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    if do_nothing:
        mock_helper.check_do_nothing()
    else:
        mock_helper.check_task_proxy(must_proxy=False)


# Тест проверяет, что мы смотрим на использованные терминалы при выборе
# фолбэка. Может быть так, что фолбэк использовали два раза, а терминал для
# этого фолбэка уже три раза. И если мы выставили кол-во попыток для фолбэка
# равное трем, то мы не должны использовать фолбэк в третий раз, потому что
# по факту терминал был уже использован три раза.
@pytest.mark.parametrize('retries_count, must_proxy', [(3, True), (4, False)])
async def test_terminal_id_in_first_attempt(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        retries_count,
        must_proxy,
):
    used_terminal_id = '2809'
    used_fallback_name = 'from_payture_to_sberbank'

    operations = ['create:1', 'create:1:attempt:1', 'create:1:attempt:2']
    terminals = [used_terminal_id, used_terminal_id, used_terminal_id]
    fallback_names = [None, used_fallback_name, used_fallback_name]

    for operation_id, terminal_id, fallback_name in zip(
            operations, terminals, fallback_names,
    ):
        mock_helper.add_attempt(
            operation_id,
            FAIL,
            terminal_id=terminal_id,
            fallback_name=fallback_name,
        )
    mock_helper.mock_retrieve()

    mock_helper.add_fallback(
        terminal_id=used_terminal_id,
        fallback_name=used_fallback_name,
        retries_count=retries_count,
    )

    await run_payments_fallback_proxy_stq(
        operation_id=operations[-1],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет случай, когда у нас есть несколько фолбэков на выбор.
# Мы должны посмотреть на все использованные терминалы и на все
# использованные фолбэки, при выборе новой попытки.
@pytest.mark.parametrize('retries_count, must_proxy', [(2, False), (1, True)])
async def test_several_fallbacks(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        mock_helper,
        retries_count,
        must_proxy,
):
    operations = []
    terminals = []
    fallback_names = []

    for idx in range(5):
        operations.append(f'create:1:attempt:{idx}')
        terminals.append(str(uuid.uuid4()))
        fallback_names.append(str(uuid.uuid4()))

    operations[0] = 'create:1'
    fallback_names[0] = None

    for operation_id, terminal_id, fallback_name in zip(
            operations, terminals, fallback_names,
    ):
        mock_helper.add_attempt(
            operation_id,
            FAIL,
            terminal_id=terminal_id,
            fallback_name=fallback_name,
        )

        mock_helper.add_fallback(
            terminal_id=terminal_id,
            fallback_name=fallback_name,
            retries_count=retries_count,
        )
    mock_helper.mock_retrieve()

    await run_payments_fallback_proxy_stq(
        operation_id=operations[-1],
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
    )

    mock_helper.check_task_proxy(must_proxy=must_proxy)


# Тест проверяет проксирование таски, если фолбеков не найдено.
async def test_proxy_if_fallback_not_exist(
        grocery_orders, run_payments_fallback_proxy_stq, mock_helper,
):
    operation_id = 'create:1'

    mock_helper.add_attempt(operation_id, status=FAIL)
    mock_helper.mock_retrieve()

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
        transactions=[mock_helper.get_callback_transaction(0)],
    )

    mock_helper.check_task_proxy(
        must_proxy=True,
        operation_id=operation_id,
        operation_status=FAIL,
        notification_type=consts.OPERATION_FINISH,
        transactions=[mock_helper.get_callback_transaction(0)],
    )


# Если все фолбэки зафейлились, то мы проксируем в
# grocery_payments_transactions_callback только первую попытку.
# Про остальные попытки мы игнорируем.
async def test_proxy_main_if_fallback_failed(
        grocery_orders, run_payments_fallback_proxy_stq, mock_helper,
):
    operation_id = 'create:1'
    operation_id_retry = operation_id + ':attempt:1'

    mock_helper.add_attempt(operation_id, status=FAIL)
    mock_helper.add_attempt(operation_id_retry, status=FAIL)
    mock_helper.mock_retrieve()

    await run_payments_fallback_proxy_stq(
        operation_id=operation_id_retry,
        notification_type=consts.OPERATION_FINISH,
        operation_status=FAIL,
        transactions=[mock_helper.get_callback_transaction(1)],
    )

    mock_helper.check_task_proxy(
        must_proxy=True,
        operation_id=operation_id,
        operation_status=FAIL,
        notification_type=consts.OPERATION_FINISH,
        transactions=[mock_helper.get_callback_transaction(0)],
    )


# Тест проверяет логику метрики для фолбэков.
@configs.PROCESSING_META
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            dict(
                attempt_1=dict(
                    op_id='create:1',
                    terminal_id=consts.PAYTURE_TERMINAL_ID,
                    status=FAIL,
                ),
                attempt_2=dict(
                    op_id='create:1:attempt:1',
                    terminal_id=consts.SBERBANK_TERMINAL_ID,
                    fallback_name=PAYTURE_TO_SBER_FALLBACK_NAME,
                    status=DONE,
                ),
                from_to_label=PAYTURE_TO_SBER_LABEL,
                success_label='success',
                should_be_collected=True,
            ),
            id='success_fallback_from_payture_to_sber',
        ),
        pytest.param(
            dict(
                attempt_1=dict(
                    op_id='create:1',
                    terminal_id=consts.PAYTURE_TERMINAL_ID,
                    status=FAIL,
                ),
                attempt_2=dict(
                    op_id='update:2',
                    terminal_id=consts.SBERBANK_TERMINAL_ID,
                    status=DONE,
                ),
                should_be_collected=False,
            ),
            id='not_retry',
        ),
        pytest.param(
            dict(
                attempt_1=dict(
                    op_id='create:1',
                    terminal_id=consts.PAYTURE_TERMINAL_ID,
                    status=FAIL,
                ),
                attempt_2=dict(
                    op_id='create:1:attempt:1',
                    terminal_id=consts.SBERBANK_TERMINAL_ID,
                    fallback_name=PAYTURE_TO_SBER_FALLBACK_NAME,
                    status=FAIL,
                ),
                from_to_label=PAYTURE_TO_SBER_LABEL,
                success_label='fail',
                should_be_collected=True,
            ),
            id='fail_fallback_from_payture_to_sber',
        ),
        pytest.param(
            dict(
                attempt_1=dict(
                    op_id='create:1',
                    terminal_id=consts.PAYTURE_TERMINAL_ID,
                    status=FAIL,
                ),
                attempt_2=dict(
                    op_id='create:1:attempt:1',
                    terminal_id=consts.TERMINAL_ID,
                    fallback_name=FALLBACK_NAME,
                    status=DONE,
                ),
                from_to_label=PAYTURE_TO_UNKNOWN_LABEL,
                success_label='success',
                should_be_collected=True,
            ),
            id='success_fallback_from_payture_to_unknown_processing',
        ),
        pytest.param(
            dict(
                attempt_1=dict(
                    op_id='create:1:attempt:3',
                    terminal_id=consts.PAYTURE_TERMINAL_ID,
                    status=FAIL,
                ),
                attempt_2=dict(
                    op_id='create:1:attempt:4',
                    terminal_id=consts.TERMINAL_ID,
                    fallback_name=PAYTURE_TO_SBER_FALLBACK_NAME,
                    status=DONE,
                ),
                from_to_label=PAYTURE_TO_UNKNOWN_LABEL,
                success_label='success',
                should_be_collected=True,
            ),
            id='two_retries_in_row',
        ),
    ],
)
async def test_fallback_metrics(
        grocery_orders,
        run_payments_fallback_proxy_stq,
        taxi_grocery_payments_monitor,
        mock_helper,
        params,
):
    op_1 = params['attempt_1']['op_id']
    op_2 = params['attempt_2']['op_id']

    op_1_status = params['attempt_1']['status']
    op_2_status = params['attempt_2']['status']

    op_1_terminal_id = params['attempt_1']['terminal_id']
    op_2_terminal_id = params['attempt_2']['terminal_id']

    last_fallback_name = params['attempt_2'].get('fallback_name', None)

    mock_helper.add_attempt(
        op_1, status=op_1_status, terminal_id=op_1_terminal_id,
    )
    mock_helper.add_attempt(
        op_2,
        status=op_2_status,
        terminal_id=op_2_terminal_id,
        fallback_name=last_fallback_name,
    )
    mock_helper.mock_retrieve()
    mock_helper.add_fallback()

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_FALLBACK_METRICS,
    ) as collector:
        await run_payments_fallback_proxy_stq(
            operation_id=op_2,
            notification_type=consts.OPERATION_FINISH,
            operation_status=op_2_status,
        )

    metric = collector.get_single_collected_metric()
    if not params['should_be_collected']:
        assert metric is None
        return

    assert metric.value == 1
    assert metric.labels == {
        'country': COUNTRY.name,
        'from_to': params['from_to_label'],
        'status': params['success_label'],
        'sensor': 'grocery_payments_fallback_proxy_metrics',
        'fallback_name': last_fallback_name,
        'error_code': ERROR_REASON_CODE,
    }
