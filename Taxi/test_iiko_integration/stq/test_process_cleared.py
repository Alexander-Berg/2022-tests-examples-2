import dataclasses
import datetime
from typing import Any
from typing import Optional

import pytest

from generated.clients import eda_billing
from generated.clients import eda_receipts
from taxi.clients import personal

from iiko_integration.logic import users as users_module
from iiko_integration.stq import process_cleared
from test_iiko_integration import eda_stubs
from test_iiko_integration import stubs
from test_iiko_integration import transactions_stubs as tr_stubs

NOW = datetime.datetime(2042, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)

EVENT_AT = '2020-08-20T20:00:00+00:00'

ORDER_FIELDS = ['changelog']

CONFIG_REST_GROUP = stubs.CONFIG_RESTAURANT_GROUP_INFO
CONFIG_REST = stubs.CONFIG_RESTAURANT_INFO

EMAIL_INFO = {'userEmail': 'user@yandex.ru'}

PHONE_INFO = {'userPhone': '+79991112233'}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=CONFIG_REST_GROUP,
        IIKO_INTEGRATION_RESTAURANT_INFO=CONFIG_REST,
        TVM_RULES=[
            {'src': 'iiko-integration', 'dst': 'personal'},
            {'src': 'iiko-integration', 'dst': 'user-api'},
        ],
    ),
]


class DbChecker:

    # pylint: disable=attribute-defined-outside-init
    async def init_db_order(self, invoice_id, get_db_order):
        self.get_db_order = get_db_order
        self.invoice_id = invoice_id
        self.initial_order = await get_db_order(
            fields=ORDER_FIELDS, invoice_id=invoice_id,
        )
        self.cashback_percentage = 0
        cashback_percentage = await get_db_order(
            fields=['expected_cashback_percentage'], invoice_id=invoice_id,
        )
        if cashback_percentage:
            self.cashback_percentage = cashback_percentage.get(
                'expected_cashback_percentage', 0,
            )

    async def _check_order(self, expected_order):
        order = await self.get_db_order(
            fields=ORDER_FIELDS, invoice_id=self.invoice_id,
        )
        if order:
            for index, change_event in enumerate(expected_order['changelog']):
                change_event['updated_at'] = order['changelog'][index][
                    'updated_at'
                ]
        assert order == expected_order

    async def check_after(self):
        pass


class DbOrderIsNotChanged(DbChecker):
    async def check_after(self):
        await self._check_order(self.initial_order)


class DbOrderIsChanged(DbChecker):
    def __init__(self, event_version):
        self.event_version = event_version

    async def check_after(self):
        expected_order = self.initial_order
        event = expected_order['changelog'][self.event_version - 1]
        event['status'] = 'done'
        if self.cashback_percentage > 0:
            event['status'] = 'processing_extra'
        event['updated_at'] = NOW
        await self._check_order(expected_order)


@dataclasses.dataclass
class MockChecker:
    mock: Any
    times_called: int

    def check_calls(self):
        assert self.mock.times_called == self.times_called


def one_call_mock_checker(mock: Any, called: bool) -> 'MockChecker':
    return MockChecker(mock=mock, times_called=1 if called else 0)


@dataclasses.dataclass
class EdaMockChecker:
    billing_storage_create_checker: MockChecker
    receipts_send_checker: MockChecker

    def check_calls(self):
        self.billing_storage_create_checker.check_calls()
        self.receipts_send_checker.check_calls()


class NotError:
    pass


def get_payout_order(
        order_nr: str,
        event_type: str,
        event_id: str,
        amount: str,
        is_complement: bool,
):
    if is_complement:
        payment_event_type = 'yandex_account_withdraw'
    else:
        payment_event_type = 'yandex_account_topup'

    if event_type == 'refund':
        transaction_type = 'refund'
    else:
        transaction_type = 'payment'

    payment_terminal_id = 'terminal_id'
    if is_complement:
        payment_terminal_id = 'complement_terminal_id'

    return dict(
        identity=event_id,
        payment_terminal_id=payment_terminal_id,
        payment_type=payment_event_type,
        service_order_id=order_nr,
        value_amount=amount,
        dt=EVENT_AT,
        client_id=82058879,
        currency='RUB',
        commission='0.00',
        paysys_partner_id='yaeda',
        product='native_delivery',
        service_id=645,
        transaction_type=transaction_type,
        payload=[],
    )


@pytest.fixture(name='mock_eda')
def mock_eda_fixture(mockserver):
    def _mock_eda_fixture(
            order_case: str,
            event_type: str,
            event_version: int,
            main_event_amount: Optional[str] = None,
            complement_event_amount: Optional[str] = None,
            items: Optional[list] = None,
            user_info: Optional[dict] = None,
            eda_notified: bool = True,
            storage_create_response_code: int = 200,
            receipts_send_response_code: int = 200,
    ):
        if items is None:
            items = eda_stubs.CHARGE_ITEMS
        if user_info is None:
            user_info = EMAIL_INFO

        order_nr = f'invoice_{order_case}'
        main_event_id = (
            f'invoice_{order_case}_{event_type}_{event_version}_'
            f'restaurant_{order_case}'
        )
        complement_event_id = f'{main_event_id}_complement'
        complement_cashback_event_id = f'{complement_event_id}_cashback'

        data = dict(
            order_nr=order_nr,
            currency='RUB',
            place_id='1',
            commission_type='cashless',
        )
        event_types = []
        if event_type == 'charge':
            if main_event_amount:
                event_types.append('QRPaymentReceived')
            if complement_event_amount:
                event_types.append('QRPersonalWalletPaymentReceived')
                event_types.append('PayoutOrder')
                data_payout = get_payout_order(
                    order_nr,
                    event_type,
                    complement_cashback_event_id,
                    complement_event_amount,
                    is_complement=True,
                )
            data['payment_received_at'] = EVENT_AT
        else:
            if main_event_amount:
                event_types.append('QRRefund')
            if complement_event_amount:
                event_types.append('QRPersonalWalletRefund')
                event_types.append('PayoutOrder')
                data_payout = get_payout_order(
                    order_nr,
                    event_type,
                    complement_cashback_event_id,
                    complement_event_amount,
                    is_complement=True,
                )

            data['refunded_at'] = EVENT_AT

        @mockserver.json_handler(
            '/eda-billing/internal-api/v1/billing-storage/create/bulk',
        )
        def _billing_storage_create(request):
            for item in request.json:
                assert item['kind'] in event_types

                exp_data = data
                if item['kind'] in [
                        'QRPersonalWalletPaymentReceived',
                        'QRPersonalWalletRefund',
                ]:
                    exp_data['amount'] = complement_event_amount
                    exp_data['payment_terminal_id'] = 'complement_terminal_id'
                    event_id = complement_event_id
                elif item['kind'] in ['QRPaymentReceived', 'QRRefund']:
                    exp_data['payment_terminal_id'] = 'terminal_id'
                    exp_data['amount'] = main_event_amount
                    event_id = main_event_id
                elif item['kind'] == 'PayoutOrder':
                    exp_data = data_payout
                    event_id = complement_cashback_event_id

                item.pop('kind')
                assert item == dict(
                    data=exp_data,
                    event_at=EVENT_AT,
                    external_event_ref=event_id,
                    external_obj_id=order_nr,
                    service_user_id='',
                    status='new',
                    tags=[],
                    service='restaurants',
                    journal_entries=[],
                )
            return mockserver.make_response(
                status=storage_create_response_code, json={},
            )

        is_refund = event_type != 'charge'

        order = dict(
            orderNr=order_nr,
            countryCode='RU',
            paymentMethod='card',
            orderType='QR_pay',
        )

        @mockserver.json_handler('/eda-receipts/internal-api/v1/receipts/send')
        def _receipts_send(request):
            assert request.json == dict(
                documentId=main_event_id,
                isRefund=is_refund,
                order=order,
                products=items,
                userInfo=user_info,
            )
            return mockserver.make_response(
                status=receipts_send_response_code, json={},
            )

        if eda_notified:
            if storage_create_response_code == 500:
                billing_storage_create_calls = 3
            else:
                billing_storage_create_calls = 1
        else:
            billing_storage_create_calls = 0

        if (
                billing_storage_create_calls != 0
                and storage_create_response_code == 200
        ):
            receipts_send_times_calls = 1
        else:
            receipts_send_times_calls = 0

        return EdaMockChecker(
            billing_storage_create_checker=MockChecker(
                mock=_billing_storage_create,
                times_called=billing_storage_create_calls,
            ),
            receipts_send_checker=MockChecker(
                mock=_receipts_send, times_called=receipts_send_times_calls,
            ),
        )

    return _mock_eda_fixture


@dataclasses.dataclass
class UserInfoMockChecker:
    get_email_id_checker: MockChecker
    get_email_checker: MockChecker
    get_phone_id_checker: MockChecker
    get_phone_checker: MockChecker

    def check_calls(self):
        self.get_email_id_checker.check_calls()
        self.get_email_checker.check_calls()
        self.get_phone_id_checker.check_calls()
        self.get_phone_checker.check_calls()


@pytest.fixture(name='mock_user_info')
def mock_user_info_fixture(mockserver):
    def _mock_user_info_fixture(
            yandex_uid='123456789',
            user_info_requested=True,
            email_id_found=True,
            email_found=True,
            phone_id_found=True,
            phone_found=True,
            email_id_from_db=False,
            email_for_db_id_found=False,
    ) -> UserInfoMockChecker:
        @mockserver.json_handler('/zalogin/admin/uid-info')
        def _get_phone_id_mock(request):
            assert request.query['yandex_uid'] == yandex_uid
            if phone_id_found:
                return {
                    'yandex_uid': yandex_uid,
                    'type': 'portal',
                    'bound_phone_ids': [
                        {
                            'phone_id': 'user_phone_id',
                            'personal_phone_id': 'user_personal_phone_id',
                        },
                    ],
                    'allow_reset_password': True,
                    'has_2fa_on': True,
                    'sms_2fa_status': True,
                }
            return {
                'yandex_uid': yandex_uid,
                'type': 'portal',
                'bound_phone_ids': [],
                'allow_reset_password': True,
                'has_2fa_on': True,
                'sms_2fa_status': True,
            }

        @mockserver.json_handler('/user_api-api/user_emails/get')
        def _get_email_id(request):
            assert request.json['yandex_uids'] == [yandex_uid]
            if email_id_found:
                return {
                    'items': [
                        dict(
                            id='user_email_id',
                            personal_email_id='user_personal_email_id',
                        ),
                    ],
                }
            return {'items': []}

        error_response = mockserver.make_response(
            status=404, json={'code': 'c', 'message': 'm'},
        )

        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def _get_phone_mock(request):
            assert request.json == dict(id='user_personal_phone_id')
            if phone_found:
                return {
                    'id': 'user_personal_phone_id',
                    'value': '+79991112233',
                }
            return error_response

        @mockserver.json_handler('/personal/v1/emails/retrieve')
        def _get_email_mock(request):
            if email_id_from_db and request.json == dict(
                    id='db_personal_email_id',
            ):
                if email_for_db_id_found:
                    return {
                        'id': 'db_personal_email_id',
                        'value': 'user@yandex.ru',
                    }
                return error_response
            assert request.json == dict(id='user_personal_email_id')
            if email_found:
                return {
                    'id': 'user_personal_email_id',
                    'value': 'user@yandex.ru',
                }
            return error_response

        phone_calls = (
            user_info_requested
            and not email_id_from_db
            and (not email_id_found or not email_found)
        )

        return UserInfoMockChecker(
            get_email_id_checker=one_call_mock_checker(
                _get_email_id, user_info_requested and not email_id_from_db,
            ),
            get_email_checker=one_call_mock_checker(
                _get_email_mock,
                user_info_requested and (email_id_found or email_id_from_db),
            ),
            get_phone_id_checker=one_call_mock_checker(
                _get_phone_id_mock, phone_calls,
            ),
            get_phone_checker=one_call_mock_checker(
                _get_phone_mock, phone_calls and phone_id_found,
            ),
        )

    return _mock_user_info_fixture


@pytest.fixture(name='test_task')
def test_task_fixture(stq3_context, get_db_order):
    async def _test_task_fixture(
            order_case,
            expected_error_class=NotError,
            db_checker: DbChecker = None,
    ):
        invoice_id = f'invoice_{order_case}'
        if db_checker:
            await db_checker.init_db_order(
                invoice_id=invoice_id, get_db_order=get_db_order,
            )
        error: Any = NotError()
        try:
            await process_cleared.task(
                context=stq3_context, invoice_id=invoice_id,
            )
        # pylint: disable=broad-except
        except Exception as exc:
            error = exc
            if not isinstance(error, expected_error_class):
                raise
        assert isinstance(error, expected_error_class)

        if db_checker:
            await db_checker.check_after()

    return _test_task_fixture


@dataclasses.dataclass
class SuccessfullyCase:
    order_case: str
    event_type: str
    invoice: dict
    event_version: int
    main_event_amount: Optional[str]
    complement_event_amount: Optional[str]
    eda_items: list
    is_cashback_percentage: bool = False


@pytest.mark.parametrize(
    ['case'],
    [
        pytest.param(
            SuccessfullyCase(
                order_case='charge',
                event_type='charge',
                invoice=tr_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
                event_version=1,
                main_event_amount='300',
                complement_event_amount=None,
                eda_items=eda_stubs.CHARGE_ITEMS,
            ),
            id='notify_charge',
        ),
        pytest.param(
            SuccessfullyCase(
                order_case='charge',
                event_type='charge',
                invoice=tr_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
                event_version=1,
                main_event_amount='300',
                complement_event_amount=None,
                eda_items=eda_stubs.CHARGE_ITEMS,
                is_cashback_percentage=True,
            ),
            id='notify_charge_with_cashback',
        ),
        pytest.param(
            SuccessfullyCase(
                order_case='refund',
                event_type='refund',
                invoice=tr_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
                event_version=2,
                main_event_amount='50',
                complement_event_amount=None,
                eda_items=eda_stubs.REFUND_ITEMS,
            ),
            id='notify_refund',
        ),
        pytest.param(
            SuccessfullyCase(
                order_case='charge_complement',
                event_type='charge',
                invoice=tr_stubs.COMPOSITE_INVOICE_RETRIEVE_RESPONSE,
                event_version=1,
                main_event_amount='101',
                complement_event_amount='199',
                eda_items=eda_stubs.COMPLEMENT_CHARGE_ITEMS,
            ),
            id='notify_refund',
        ),
        pytest.param(
            SuccessfullyCase(
                order_case='refund_complement',
                event_type='refund',
                invoice=tr_stubs.COMPOSITE_INVOICE_RETRIEVE_RESPONSE,
                event_version=2,
                main_event_amount=None,
                complement_event_amount='50',
                eda_items=eda_stubs.COMPLEMENT_REFUND_ITEMS,
            ),
            id='notify_refund',
        ),
    ],
)
@pytest.mark.parametrize(
    'is_personal_email_id_in_db',
    [
        pytest.param(True, id='take persona_email_id from db'),
        pytest.param(False, id='do not take persona_email_id from db'),
    ],
)
async def test_successfully_finish(
        mock_invoice_retrieve,
        mock_eda,
        mock_user_info,
        test_task,
        pgsql,
        case: SuccessfullyCase,
        is_personal_email_id_in_db: bool,
):
    if is_personal_email_id_in_db:
        _add_personal_email_id_to_db(pgsql, case.order_case)

    if case.is_cashback_percentage:
        _add_cashback_percentage_to_db(pgsql, case.order_case)

    transactions_mock = mock_invoice_retrieve(
        invoice_id=f'invoice_{case.order_case}', response_data=case.invoice,
    )

    eda_mock = mock_eda(
        order_case=case.order_case,
        event_type=case.event_type,
        event_version=case.event_version,
        main_event_amount=case.main_event_amount,
        complement_event_amount=case.complement_event_amount,
        items=case.eda_items,
    )

    user_info_mock = mock_user_info(
        email_id_from_db=is_personal_email_id_in_db,
        email_for_db_id_found=True,
    )

    await test_task(
        order_case=case.order_case,
        db_checker=DbOrderIsChanged(case.event_version),
    )

    assert transactions_mock.times_called == 1
    user_info_mock.check_calls()
    eda_mock.check_calls()


def _add_personal_email_id_to_db(pgsql, case: str):
    invoice_id = f'invoice_{case}'
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'UPDATE iiko_integration.orders '
            f'SET personal_email_id = \'db_personal_email_id\' '
            f'WHERE invoice_id = \'{invoice_id}\';',
        )


def _add_cashback_percentage_to_db(pgsql, case: str):
    invoice_id = f'invoice_{case}'
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'UPDATE iiko_integration.orders '
            f'SET expected_cashback_percentage = 10 '
            f'WHERE invoice_id = \'{invoice_id}\';',
        )


@pytest.mark.parametrize(
    ['case', 'invoice_retrieve_code'],
    [
        pytest.param('unknown_order', 200, id='unknown_order'),
        pytest.param('refund', 404, id='invoice_not_found'),
        pytest.param('refunded', 200, id='no_current_change_event'),
    ],
)
async def test_unsuccessfully_finished(
        mock_invoice_retrieve,
        mock_eda,
        mock_user_info,
        test_task,
        case: str,
        invoice_retrieve_code: int,
):
    transactions_mock = mock_invoice_retrieve(
        invoice_id=f'invoice_{case}', response_code=invoice_retrieve_code,
    )
    eda_mock = mock_eda(
        order_case=case,
        event_type=case,
        event_version=2,
        main_event_amount='50',
        eda_notified=False,
    )
    user_inf_mock = mock_user_info(user_info_requested=False)

    await test_task(order_case=case, db_checker=DbOrderIsNotChanged())

    assert transactions_mock.times_called == 1
    eda_mock.check_calls()
    user_inf_mock.check_calls()


@pytest.mark.parametrize(
    [
        'storage_create_response_code',
        'receipts_send_response_code',
        'expected_error',
    ],
    [
        pytest.param(
            500,
            None,
            eda_billing.NotDefinedResponse,
            id='storage_create_failed',
        ),
        pytest.param(
            200,
            500,
            eda_receipts.NotDefinedResponse,
            id='receipts_send_failed',
        ),
    ],
)
async def test_eda_failed(
        mock_invoice_retrieve,
        mock_user_info,
        mock_eda,
        test_task,
        storage_create_response_code,
        receipts_send_response_code,
        expected_error,
):
    case = 'refund'
    transactions_mock = mock_invoice_retrieve(invoice_id=f'invoice_{case}')
    user_info_mock = mock_user_info()
    eda_mock = mock_eda(
        order_case=case,
        event_type=case,
        event_version=2,
        main_event_amount='50',
        items=eda_stubs.REFUND_ITEMS,
        storage_create_response_code=storage_create_response_code,
        receipts_send_response_code=receipts_send_response_code,
    )

    await test_task(
        order_case=case,
        db_checker=DbOrderIsNotChanged(),
        expected_error_class=expected_error,
    )

    assert transactions_mock.times_called == 1
    eda_mock.check_calls()
    user_info_mock.check_calls()


@pytest.mark.parametrize(
    [
        'email_id_found',
        'email_found',
        'phone_id_found',
        'phone_found',
        'email_id_from_db',
        'email_for_db_id_found',
        'expected_user_info',
    ],
    [
        pytest.param(
            True,
            True,
            False,
            False,
            False,
            False,
            EMAIL_INFO,
            id='email_found',
        ),
        pytest.param(
            False,
            True,
            True,
            True,
            False,
            False,
            PHONE_INFO,
            id='email_id_not_found',
        ),
        pytest.param(
            True,
            False,
            True,
            True,
            False,
            False,
            PHONE_INFO,
            id='email_not_found',
        ),
        pytest.param(
            False,
            False,
            False,
            True,
            False,
            False,
            None,
            id='phone_id_not_found',
        ),
        pytest.param(
            False,
            False,
            True,
            False,
            False,
            False,
            None,
            id='phone_not_found',
        ),
        pytest.param(
            True,
            False,
            False,
            False,
            True,
            True,
            EMAIL_INFO,
            id='problem request to personal with id from db',
        ),
    ],
)
async def test_user_info(
        mock_invoice_retrieve,
        mock_user_info,
        mock_eda,
        pgsql,
        test_task,
        email_id_found,
        email_found,
        phone_id_found,
        phone_found,
        email_id_from_db,
        email_for_db_id_found,
        expected_user_info,
):
    case = 'refund'
    if email_id_from_db:
        _add_personal_email_id_to_db(pgsql, case)
    transactions_mock = mock_invoice_retrieve(invoice_id=f'invoice_{case}')
    user_info_mock = mock_user_info(
        email_id_found=email_id_found,
        email_found=email_found,
        phone_id_found=phone_id_found,
        phone_found=phone_found,
        email_id_from_db=email_id_from_db,
        email_for_db_id_found=email_for_db_id_found,
    )
    eda_mock = mock_eda(
        order_case=case,
        event_type=case,
        event_version=2,
        main_event_amount='50',
        items=eda_stubs.REFUND_ITEMS,
        user_info=expected_user_info,
        eda_notified=expected_user_info is not None,
    )

    if expected_user_info:
        await test_task(order_case=case, db_checker=DbOrderIsChanged(2))
    elif email_id_from_db:
        await test_task(
            order_case=case,
            db_checker=DbOrderIsNotChanged(),
            expected_error_class=personal.BaseError,
        )
    else:
        await test_task(
            order_case=case,
            db_checker=DbOrderIsNotChanged(),
            expected_error_class=users_module.NotFoundError,
        )

    assert transactions_mock.times_called == 1
    eda_mock.check_calls()
    user_info_mock.check_calls()
