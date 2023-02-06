import datetime
import decimal

import aiohttp.web
import lxml.etree
import pytest

from testsuite.utils import http

from selfemployed.fns import client as fns_client
from selfemployed.fns import client_models
from selfemployed.generated.web import web_context as context

_RegisterIncomeType = client_models.RegisterIncomeRawModel.IncomeType
_RevertReasonCode = client_models.RevertIncomeRawModel.ReasonCode

_UTC = datetime.timezone.utc


@pytest.mark.parametrize(
    'method_name, params, expected',
    (
        (
            'bind_by_phone',
            {'phone': 'PHONE', 'permissions': ['PERM']},
            'bind_by_phone',
        ),
        (
            'bind_by_inn',
            {'inn': 'INN', 'permissions': ['PERM']},
            'bind_by_inn',
        ),
        ('unbind', {'inn': 'INN'}, 'unbind'),
        (
            'check_bind_status',
            {'request_id': 'REQUEST_ID'},
            'check_bind_status',
        ),
        ('get_details', {'inn': 'INN'}, 'get_details'),
        (
            'get_income',
            {
                'inn': 'INN',
                'from_date': datetime.datetime(2021, 1, 1),
                'to_date': datetime.datetime(2021, 5, 5),
            },
            'get_income',
        ),
        (
            'get_inn_by_personal_info',
            {
                'first_name': 'FN',
                'last_name': 'LN',
                'birthday': datetime.datetime(2021, 1, 1),
                'passport_series': 'PS',
                'passport_number': 'PN',
                'middle_name': 'MN',
            },
            'get_inn',
        ),
        ('get_permissions', {'inn': 'INN'}, 'get_permissions'),
        (
            'get_newly_unbound',
            {
                'date_from': datetime.datetime(2021, 1, 1),
                'limit': 10,
                'offset': 0,
            },
            'get_newly_unbound',
        ),
        (
            'reg_partner',
            {
                'name': 'TAXI',
                'inn': 'TAXI_INN',
                'phone': 'TAXI_PHONE',
                'jpg_base64': b'LOGO',
            },
            'reg_partner',
        ),
        (
            'register_income',
            {
                'inn': 'INN',
                'title': 'TITLE',
                'total': 100.12,
                'req_time': datetime.datetime(2021, 1, 1),
                'op_time': datetime.datetime(2021, 2, 2),
            },
            'register_income_person',
        ),
        (
            'register_income_raw',
            {
                'data': client_models.RegisterIncomeRawModel(
                    inn='INN',
                    request_time=datetime.datetime(2021, 1, 1),
                    operation_time=datetime.datetime(2021, 2, 2),
                    income_type=_RegisterIncomeType.FROM_INDIVIDUAL,
                    services=[
                        client_models.IncomeService(
                            amount=decimal.Decimal('100.12'),
                            name='TITLE',
                            quantity=1,
                        ),
                    ],
                    total_amount=decimal.Decimal('100.12'),
                ),
            },
            'register_income_person',
        ),
        (
            'register_income',
            {
                'inn': 'INN',
                'title': 'TITLE',
                'total': 100.12,
                'req_time': datetime.datetime(2021, 1, 1),
                'op_time': datetime.datetime(2021, 2, 2),
                'customer_inn': 'CINN',
                'customer_organisation': 'CORG',
            },
            'register_income_legal',
        ),
        (
            'register_income_raw',
            {
                'data': client_models.RegisterIncomeRawModel(
                    inn='INN',
                    request_time=datetime.datetime(2021, 1, 1),
                    operation_time=datetime.datetime(2021, 2, 2),
                    income_type=_RegisterIncomeType.FROM_LEGAL_ENTITY,
                    services=[
                        client_models.IncomeService(
                            amount=decimal.Decimal('100.12'),
                            name='TITLE',
                            quantity=1,
                        ),
                    ],
                    total_amount=decimal.Decimal('100.12'),
                    customer_inn='CINN',
                    customer_organization='CORG',
                ),
            },
            'register_income_legal',
        ),
        (
            'register_income',
            {
                'inn': 'INN',
                'title': 'TITLE',
                'total': 100.12,
                'req_time': datetime.datetime(2021, 1, 1),
                'op_time': datetime.datetime(2021, 2, 2),
                'idempotency_id': 'idempotency_id',
            },
            'register_income_with_idempotency',
        ),
        (
            'revert_income',
            {'inn': 'INN', 'receipt_id': 'RECEIPT_ID', 'is_refund': False},
            'revert_income',
        ),
        (
            'revert_income_raw',
            {
                'data': client_models.RevertIncomeRawModel(
                    inn='INN',
                    receipt_id='RECEIPT_ID',
                    reason_code=_RevertReasonCode.REGISTRATION_MISTAKE,
                ),
            },
            'revert_income',
        ),
        (
            'revert_income',
            {'inn': 'INN', 'receipt_id': 'RECEIPT_ID', 'is_refund': True},
            'revert_income_refund',
        ),
        (
            'revert_income_raw',
            {
                'data': client_models.RevertIncomeRawModel(
                    inn='INN',
                    receipt_id='RECEIPT_ID',
                    reason_code=_RevertReasonCode.REFUND,
                ),
            },
            'revert_income_refund',
        ),
        ('get_taxpayer_status_v2', {'inn': 'INN'}, 'get_taxpayer_status_v2'),
    ),
)
async def test_request_with_msg_id(
        se_web_context: context.Context,
        mockserver,
        load_binary,
        method_name,
        params,
        expected,
):
    expected_request = _fix_indent(load_binary(f'requests/{expected}.xml'))
    response = load_binary('responses/message_id_response.xml')

    @mockserver.handler('/SmzIntegrationService')
    async def _request(request: http.Request):
        assert request.headers['FNS-OpenApi-Token'] == 'AUTH_TOKEN'
        assert request.headers['FNS-OpenApi-UserToken'] == 'NDU2MA=='
        assert _fix_indent(request.get_data()) == expected_request
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    method = getattr(se_web_context.client_fns, method_name)
    msg_id = await method(**params)
    assert msg_id == 'MESSAGE_ID'


@pytest.mark.parametrize(
    'method_name, response_data, expected',
    (
        ('get_bind_by_inn_response', 'bind', 'BIND_ID'),
        (
            'get_unbind_response',
            'unbind',
            datetime.datetime(2021, 1, 1, tzinfo=_UTC),
        ),
        (
            'get_income_response',
            'receipts',
            (
                [
                    {
                        'link': 'LINK1',
                        'total': 123.32,
                        'receipt_id': 'RECEIPT_ID1',
                        'request_time': datetime.datetime(
                            2021, 1, 2, tzinfo=_UTC,
                        ),
                        'operation_time': datetime.datetime(
                            2021, 1, 1, tzinfo=_UTC,
                        ),
                        'cancellation_time': None,
                        'partner_code': 'PARTNER_CODE',
                    },
                    {
                        'link': 'LINK2',
                        'total': 321.12,
                        'receipt_id': 'RECEIPT_ID2',
                        'request_time': datetime.datetime(
                            2021, 2, 2, tzinfo=_UTC,
                        ),
                        'operation_time': datetime.datetime(
                            2021, 2, 1, tzinfo=_UTC,
                        ),
                        'partner_code': 'PARTNER_CODE',
                        'cancellation_time': datetime.datetime(
                            2021, 2, 3, tzinfo=_UTC,
                        ),
                    },
                ],
                False,
            ),
        ),
        ('get_details_response', 'details', ('Fn', 'Ln', 'Mn')),
        (
            'get_registration_details_response',
            'registration_details',
            (datetime.datetime(2021, 1, 1, tzinfo=_UTC), None),
        ),
        ('get_bind_status_response', 'bind_status', ('IN_PROGRESS', 'INN')),
        ('get_register_income_response', 'income', ('RECEIPT_ID', 'LINK')),
        ('get_inn_by_personal_info_response', 'inn_by_pd', ['INN1', 'INN2']),
        (
            'get_newly_unbound_response',
            'unbound',
            (
                [
                    {
                        'inn': 'INN1',
                        'timestamp': datetime.datetime(
                            2021, 1, 1, tzinfo=_UTC,
                        ),
                    },
                    {
                        'inn': 'INN2',
                        'timestamp': datetime.datetime(
                            2021, 2, 2, tzinfo=_UTC,
                        ),
                    },
                ],
                False,
            ),
        ),
        ('get_newly_unbound_response', 'unbound_empty', ([], False)),
        ('get_permissions_response', 'permissions', ['PERM1', 'PERM2']),
        ('get_revert_income_response', 'revert', 'DELETED'),
        (
            'get_partner_status_response',
            'partner_status',
            ('PARTNER_ID', datetime.datetime(2021, 1, 1, tzinfo=_UTC)),
        ),
        (
            'get_taxpayer_status_response_v2',
            'taxpayer_status_response_v2',
            client_models.TaxpayerStatus(
                first_name='Fn',
                second_name='Ln',
                middle_name='Mn',
                registration_time=datetime.datetime(2021, 1, 1, tzinfo=_UTC),
                region_oktmo_code='10000000',
                phone='PHONE',
                oksm_code='123',
            ),
        ),
    ),
)
async def test_get_and_parse_result(
        se_web_context: context.Context,
        mockserver,
        load_binary,
        method_name,
        response_data,
        expected,
):
    expected_request = _fix_indent(
        load_binary('requests/message_id_request.xml'),
    )
    response = load_binary(f'responses/{response_data}.xml')

    @mockserver.handler('/SmzIntegrationService')
    async def _request(request: http.Request):
        assert request.headers['FNS-OpenApi-Token'] == 'AUTH_TOKEN'
        assert request.headers['FNS-OpenApi-UserToken'] == 'NDU2MA=='
        assert _fix_indent(request.get_data()) == expected_request
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    method = getattr(se_web_context.client_fns, method_name)
    result = await method('MESSAGE_ID')
    assert result == expected


async def test_unauthenticated(
        se_web_context: context.Context, mockserver, load_binary,
):
    expected_request = _fix_indent(load_binary('requests/unbind.xml'))
    response = load_binary(f'responses/unauthenticated.xml')

    @mockserver.handler('/SmzIntegrationService')
    async def _request(request: http.Request):
        assert request.headers['FNS-OpenApi-Token'] == 'AUTH_TOKEN'
        assert request.headers['FNS-OpenApi-UserToken'] == 'NDU2MA=='
        assert _fix_indent(request.get_data()) == expected_request
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    with pytest.raises(fns_client.AuthFail):
        # AuthFail can only be thrown on initial request
        # TODO: check auth error in get_response
        await se_web_context.client_fns.unbind('INN')


@pytest.mark.parametrize(
    'request_data, error_type, code, additional',
    (
        (
            'taxpayer_unregistered',
            fns_client.TaxpayerUnregisteredError,
            'TAXPAYER_UNREGISTERED',
            {},
        ),
        ('partner_deny', fns_client.SmzPlatformError, 'PARTNER_DENY', {}),
        (
            'permission_not_granted',
            fns_client.SmzPlatformError,
            'PERMISSION_NOT_GRANTED',
            {},
        ),
        (
            'request_validation_error',
            fns_client.RequestValidationError,
            'REQUEST_VALIDATION_ERROR',
            {},
        ),
        (
            'duplicate',
            fns_client.DuplicateReceiptPlatformError,
            'DUPLICATE',
            {'RECEIPT_URL': 'LINK', 'RECEIPT_ID': 'ID'},
        ),
        (
            'taxpayer_unbound',
            fns_client.SmzPlatformError,
            'TAXPAYER_UNBOUND',
            {'INN': 'INN'},
        ),
        (
            'taxpayer_already_bound',
            fns_client.TaxpayerAlreadyBoundError,
            'TAXPAYER_ALREADY_BOUND',
            {'INN': 'INN'},
        ),
        (
            'taxpayer_not_found',
            fns_client.TaxpayerNotFoundError,
            'TAXPAYER_NOT_FOUND',
            {},
        ),
        ('internal_error', fns_client.SmzPlatformError, 'INTERNAL_ERROR', {}),
    ),
)
async def test_error_response(
        se_web_context: context.Context,
        mockserver,
        load_binary,
        request_data,
        error_type,
        code,
        additional,
):
    expected_request = _fix_indent(
        load_binary('requests/message_id_request.xml'),
    )
    response = load_binary(f'responses/{request_data}.xml')

    @mockserver.handler('/SmzIntegrationService')
    async def _request(request: http.Request):
        assert request.headers['FNS-OpenApi-Token'] == 'AUTH_TOKEN'
        assert request.headers['FNS-OpenApi-UserToken'] == 'NDU2MA=='
        assert _fix_indent(request.get_data()) == expected_request
        return aiohttp.web.Response(
            body=response, content_type='application/xml',
        )

    with pytest.raises(error_type) as error:
        await se_web_context.client_fns.get_details_response('MESSAGE_ID')

    assert error.value.code == code
    print(code, error.value.additional)


async def test_bad_error_response(
        se_web_context: context.Context, mockserver, load_binary,
):
    response = load_binary(f'responses/bad.html')

    @mockserver.handler('/SmzIntegrationService')
    async def _request(request: http.Request):
        assert request.headers['FNS-OpenApi-Token'] == 'AUTH_TOKEN'
        assert request.headers['FNS-OpenApi-UserToken'] == 'NDU2MA=='
        return aiohttp.web.Response(
            status=500, body=response, content_type='text/html',
        )

    with pytest.raises(fns_client.ErrorFromServer):
        await se_web_context.client_fns.get_details_response('MESSAGE_ID')


def _fix_indent(xml_data: bytes) -> bytes:
    etree = lxml.etree.fromstring(xml_data)
    # default pretty_print=False keeps indents from source
    return lxml.etree.tostring(etree, pretty_print=True)
