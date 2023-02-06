# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name, too-many-lines
import base64
import copy
import dataclasses
import datetime
import json
import typing as tp
import urllib
import uuid

import bson
from cargo_claims_plugins import *  # noqa: F403 F401
import dateutil
import pytest
import pytz

from testsuite.utils import matching

YANDEX_UID = 'user_id'
REMOTE_IP = '0.0.0.0'

PROFILE_REQUEST_1 = {
    'user': {'personal_phone_id': '+71111111111_id'},
    'name': 'string',
    'sourceid': 'cargo',
}

PROFILE_REQUEST_2 = {
    'user': {'personal_phone_id': '+79999999991_id'},
    'name': 'string',
    'sourceid': 'cargo',
}

PROFILE_RESPONSE = {
    'dont_ask_name': False,
    'experiments': [],
    'name': 'Насруло',
    'personal_phone_id': 'personal_phone_id_1',
    'user_id': 'taxi_user_id_1',
}

CHANGEDESTINATIONS_RESPONSE = {
    'change_id': '3a78e3efbffb4700b8649c109e62b451',
    'name': 'comment ',
    'status': 'success',
    'value': [
        {
            'type': 'address',
            'country': 'Россия',
            'fullname': 'Россия, Москва, 8 Марта, 4',
            'geopoint': [33.1, 52.1],
            'locality': 'Москва',
            'porchnumber': '',
            'premisenumber': '4',
            'thoroughfare': '8 Марта',
        },
    ],
}

ISO8601_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

CARGO_ORDER_ID = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'

TAXIMETER_STATUS_BY_STATUS = {
    'performer_found': 'new',
    'pickup_arrived': 'new',
    'pickuped': 'delivering',
    'delivery_arrived': 'delivering',
    'ready_for_pickup_confirmation': 'pickup_confirmation',
    'ready_for_delivery_confirmation': 'droppof_confirmation',
    'pay_waiting': 'droppof_confirmation',
    'ready_for_return_confirmation': 'return_confirmation',
    'return_arrived': 'returning',
    'returning': 'returning',
    'cancelled': 'complete',
    'cancelled_with_payment': 'complete',
    'cancelled_by_taxi': 'complete',
    'delivered': 'complete',
    'returned': 'complete',
    'cancelled_with_items_on_hands': 'complete',
}
DRIVER_INFO = {
    'park_id': 'some_park',
    'driver_profile_id': 'some_driver',
    'taximeter_app': {
        'version': '9.09',
        'version_type': 'dev',
        'platform': 'android',
    },
}

_CARGO_EXTENDED_LOOKUP_MERGE_TAG = [
    {
        'consumer': 'cargo-claims/segment-info',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_extended_lookup',
    },
    {
        'consumer': 'cargo-claims/active-performer-lookup-claims-cache',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_extended_lookup',
    },
]

GROCERY_DISPATCH_DEPOT_CACHE = ['lavka', 'lavka1', 'lavka2']

NO_PRICING_CALC_ID = 'no-pricing/v1'

DEFAULT_BRAND_ID = 123654


# pylint: disable=invalid-name
@dataclasses.dataclass(frozen=True)
class ProcessingEvent:
    id: str
    idempotency_token: str
    payload: dict


@pytest.fixture(name='query_processing_events')
def _query_processing_events(pgsql):
    def _wrapper(claim_id: str):
        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            """
            SELECT id, idempotency_token, payload
            FROM cargo_claims.processing_events
            WHERE item_id =  %s
            """,
            (claim_id,),
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(
                ProcessingEvent(
                    id=row[0], idempotency_token=row[1], payload=row[2],
                ),
            )
        return result

    return _wrapper


@pytest.fixture(name='enable_billing_event_feature')
async def _enable_billing_event_feature(taxi_cargo_claims, experiments3):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_taxi_park_billing_event',
            consumers=['cargo-claims/create-claim'],
            clauses=[],
            default_value={'enabled': True},
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


@pytest.fixture(name='enable_using_cargo_pipelines_feature')
async def _enable_using_cargo_pipelines_feature(
        taxi_cargo_claims, experiments3,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_using_cargo_pipelines',
            consumers=['cargo-claims/create-claim'],
            clauses=[],
            default_value={'enabled': True},
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


@pytest.fixture(name='enable_dry_run_in_cargo_pipelines')
async def _enable_dry_run_in_cargo_pipelines(taxi_cargo_claims, experiments3):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_use_cargo_pipelines_in_dry_run',
            consumers=['cargo-claims/create-claim'],
            clauses=[],
            default_value={'enabled': True},
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


@pytest.fixture(name='extract_oldest_event_lag')
def _extract_oldest_event_lag():
    def _wrapper(result, milliseconds=None):
        if milliseconds:
            assert result['stats']['oldest-event-lag-ms'] == milliseconds
        result['stats'].pop('oldest-event-lag-ms')
        return result

    return _wrapper


@pytest.fixture(name='check_processing_stats')
async def _check_processing_stats(taxi_cargo_claims_monitor):
    async def _wrapper(
            result,
            for_processing_cnt,
            failed_cnt,
            processed_in_stq,
            stq_success=None,
            skipped_events=None,
    ):
        assert 'db-retrieve-duration-ms' in result['stats']
        result['stats'].pop('db-retrieve-duration-ms', None)
        assert 'events-split-by-coroutine-ms' in result['stats']
        result['stats'].pop('events-split-by-coroutine-ms', None)
        assert 'job-iteration-duration-ms' in result['stats']
        result['stats'].pop('job-iteration-duration-ms', None)
        assert 'single-event-processing-duration-ms' in result['stats']
        result['stats'].pop('single-event-processing-duration-ms', None)
        assert 'set-stq-fail' in result['stats']
        result['stats'].pop('set-stq-fail', None)
        assert 'stq-success' in result['stats']
        assert 'skipped-events' in result['stats']

        if skipped_events is not None:
            assert result['stats']['skipped-events'] == skipped_events
        if stq_success is not None:
            assert result['stats']['stq-success'] == stq_success
        result['stats'].pop('stq-success', None)
        result['stats'].pop('skipped-events', None)
        result['stats'].pop('processed-events', None)
        assert result == {
            'stats': {
                'events-for-processing': for_processing_cnt,
                'failed-processing': failed_cnt,
            },
        }
        stats = await taxi_cargo_claims_monitor.get_metric(
            'cargo-claims-processing-events',
        )
        assert stats['stats']['processed-in-stq-events'] == processed_in_stq

    return _wrapper


@pytest.fixture(name='taximeter_xservice', autouse=True)
def _taximeter_xservice(mockserver):
    class Context:
        def __init__(self):
            self.custom_response = None
            self.handler_change_status = None

    ctx = Context()

    @mockserver.json_handler('/taximeter-xservice/utils/order/change_status')
    def _change_status(request):
        assert request.query['origin'] == 'cargo'

        requested_taxi_status = request.json.get('status')
        assert requested_taxi_status

        if ctx.custom_response:
            return ctx.custom_response
        return {'status': requested_taxi_status}

    ctx.handler_change_status = _change_status

    return ctx


@pytest.fixture(autouse=True)
def sticker(mockserver):
    @mockserver.handler('/sticker/send/')
    def _mock_sticker_send(request, *args, **kwargs):
        return mockserver.make_response('{}', status=200)


@pytest.fixture(autouse=True)
def corp_int_api_request(mockserver):
    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {},
        }


@pytest.fixture(autouse=True)
def billing_replication_request(mockserver):
    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        return [
            {
                'ID': 100,
                'IS_ACTIVE': 1,
                'EXTERNAL_ID': '42131 /12',
                'DT': '01-01-2020',
                'SERVICES': [650, 35],
                'PERSON_ID': 100,
            },
        ]

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        return [
            {
                'ID': request.query['client_id'],
                'LONGNAME': 'ООО КАРГО_full',
                'NAME': 'ООО КАРГО_short',
            },
        ]


@pytest.fixture(autouse=True)
def dispatch_depot_cache(mockserver):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/grocery-shifts/depots',
    )
    def _mock_grocery_shifts_depots(request):
        return {'depot_ids': GROCERY_DISPATCH_DEPOT_CACHE}


@pytest.fixture
async def claim_creator(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_idempotency_token,
):
    async def wrapper(
            request_id=None, request=None, headers=None, language=None,
    ):
        if request_id is None:
            request_id = get_default_idempotency_token
        if request is None:
            request = get_default_request()
        if headers is None:
            headers = get_default_headers()
        if language:
            headers['Accept-Language'] = language
        response = await taxi_cargo_claims.post(
            f'/api/integration/v1/claims/create',
            params={'request_id': request_id},
            json=request,
            headers=headers,
        )

        return response

    yield wrapper


@pytest.fixture
async def claim_creator_v2(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        mock_payment_create,
):
    async def wrapper(request, request_id=None, headers=None, language=None):
        if request_id is None:
            request_id = get_default_idempotency_token
        if headers is None:
            headers = get_default_headers()
        if language:
            headers['Accept-Language'] = language
        response = await taxi_cargo_claims.post(
            f'/api/integration/v2/claims/create',
            params={'request_id': request_id},
            json=request,
            headers=headers,
        )

        return response

    yield wrapper


@pytest.fixture(autouse=True)
def esignature_issuer(mockserver):
    valid_code = '123456'

    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def _signature_create(request):
        assert request.headers['Accept-language']
        return mockserver.make_response('{}', status=200)

    @mockserver.json_handler('/esignature-issuer/v1/signatures/confirm')
    def _signature_confirm(request):
        if request.json['code'] == valid_code:
            return mockserver.make_response(
                json.dumps({'status': 'ok'}), status=200,
            )

        return mockserver.make_response(
            json.dumps({'status': 'invalid_code'}), status=200,
        )

    @mockserver.json_handler('/esignature-issuer/v1/signatures/list')
    def _signature_list(request):
        return {
            'doc_type': request.json['doc_type'],
            'doc_id': request.json['doc_id'],
            'signatures': [],
        }


@pytest.fixture(autouse=True)
def active_contracts(mockserver):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _mock_active_contracts(request):
        return mockserver.make_response(
            json=[{'ID': 111, 'PERSON_ID': 42}], status=200,
        )


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
    def _store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    def _bulk_store(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append(
                {'id': i['value'] + '_id', 'value': i['value']},
            )
        return result

    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id'][:-3]}

    def _bulk_retrieve(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append({'id': i['id'], 'value': i['id'][:-3]})
        return result

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    def _yandex_logins_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def _emails_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _emails_retrieve(request):
        assert request.json['id'] != ''
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
    def _yandex_logins_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_bulk_retrieve(request):
        for email_id in request.json['items']:
            assert email_id['id'] != ''
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
    def _yandex_logins_bulk_retrieve(request):
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _identifications_retrieve(request):
        return _retrieve(request)


@pytest.fixture(autouse=True)
def order_cancel(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/orders/cancel')
    def _order_cancel(request):
        return {}

    return _order_cancel


@pytest.fixture(name='mock_ucommunications')
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def send_sms(request):
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    return send_sms


@pytest.fixture(name='mock_cargo_matcher')
def _mock_cargo_matcher(mockserver, get_start_headers, load_json):
    @mockserver.json_handler('/cargo-matcher/v1/client-cars')
    def cargo_matcher(request):
        assert (
            request.json['corp_client_id']
            == get_start_headers()['X-B2B-Client-Id']
        )
        assert request.json['point_a'] == [37.588472, 55.733996]
        return load_json('cargo_matcher_response.json')

    return cargo_matcher


@pytest.fixture(name='yamaps_get_geo_objects')
def _get_geo_objects_callback(yamaps, load_json):
    @yamaps.set_fmt_geo_objects_callback
    def callback(request):
        assert request.args.get('ms') == 'pb'
        assert request.args.get('type') == 'geo'
        assert (
            urllib.parse.unquote(request.args.get('text'))
            == 'Москва, Пятницкое шоссе, 23к2'
        )
        return [load_json('yamaps_response.json')]

    return callback


@pytest.fixture(autouse=True)
def int_api(mockserver):
    class Context:
        def __init__(self):
            self.handler_profile = None
            self.handler_changedestinations = None

    ctx = Context()

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):

        assert (
            request.json == PROFILE_REQUEST_1
            or request.json == PROFILE_REQUEST_2
        )
        return PROFILE_RESPONSE

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert request.json['id'] == PROFILE_RESPONSE['user_id']
        assert (
            request.json['orderid'] == 'taxi_order_id_1'
            or request.json['orderid'] == 'taxi_order_id'
        )
        return CHANGEDESTINATIONS_RESPONSE

    ctx.handler_profile = _profile
    ctx.handler_changedestinations = _changedestinations

    return ctx


@pytest.fixture(name='mock_cargo_corp', autouse=True)
def _mock_cargo_corp(mockserver):
    class Context:
        def __init__(self):
            self.is_cargo_corp_down = True
            self.is_agent_scheme = True
            self.handler_client_traits = None

    ctx = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/traits',
    )
    def _mock_cargo_corp_client_traits(request):
        assert request.headers['X-B2B-Client-Id']
        if ctx.is_cargo_corp_down:
            return mockserver.make_response(status=500)
        return mockserver.make_response(
            status=200, json={'is_small_business': ctx.is_agent_scheme},
        )

    ctx.handler_client_traits = _mock_cargo_corp_client_traits

    return ctx


@pytest.fixture(name='mock_cargo_corp_up')
def _mock_cargo_corp_up(mock_cargo_corp):
    mock_cargo_corp.is_cargo_corp_down = False
    return mock_cargo_corp


@pytest.fixture(name='mock_cargo_finance')
def _mock_cargo_finance(mockserver):
    class Context:
        def __init__(self):
            self.method_id = None
            self.mock = None

    context = Context()

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def _mock_cargo_finance_payment_methods(request):
        response = {
            'methods': [
                {
                    'id': context.method_id,
                    'display': {
                        'type': 'cargocorp',
                        'image_tag': '',
                        'title': 'corp_name',
                    },
                    'details': {
                        'type': 'contract',
                        'corp_client_id': '123',
                        'billing_id': '456',
                        'contract_id': '789',
                        'is_logistic_contract': True,
                        'is_disabled': False,
                        'country': 'RUS',
                    },
                },
            ],
        }
        return mockserver.make_response(status=200, json=response)

    context.mock = _mock_cargo_finance_payment_methods

    return context


@pytest.fixture(name='changedestinations')
def _changedestinations(mockserver):
    def _impl(taxi_order_id='taxi_order_id_1'):
        @mockserver.json_handler('/int-authproxy/v1/changedestinations')
        def changedestinations_impl(request):
            assert request.json['id'] == PROFILE_RESPONSE['user_id']
            assert request.json['orderid'] == taxi_order_id
            return CHANGEDESTINATIONS_RESPONSE

        return changedestinations_impl

    return _impl


# Direct fixture call workaround, see CARGODEV-1325
@pytest.fixture(name='get_default_headers')
def _get_default_headers_fixture():
    return _get_default_headers()


def get_default_accept_language():
    return 'en-US;q=1, ru;q=0.8'


@pytest.fixture(name='get_default_accept_language')
def _get_default_accept_language():
    return get_default_accept_language()


def _get_default_headers():
    def _wrapper(corp_client_id=None, is_phoenix_corp=False, **kwargs):
        if corp_client_id is None:
            corp_client_id = get_default_corp_client_id()
        return {
            'X-B2B-Client-Id': corp_client_id,
            'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
            'X-B2B-Client-Storage': 'cargo' if is_phoenix_corp else 'taxi',
            'Accept-Language': get_default_accept_language(),
            'X-Yandex-UID': YANDEX_UID,
            'X-Remote-IP': REMOTE_IP,
            'X-Yandex-Login': 'abacaba',
        }

    return _wrapper


@pytest.fixture(name='get_apply_changes_headers')
def _get_apply_changes_headers_fixture(get_default_headers):
    return _get_apply_changes_headers()


def _get_apply_changes_headers():
    def _wrapper(get_default_headers, **kwargs):
        headers = get_default_headers()
        headers.update({'X-Idempotency-Token': '123456'})
        return headers

    return _wrapper


def get_default_c2c_request_v2(with_size=True, **kwargs):
    from . import utils_v2
    request = utils_v2.get_create_request()
    request['c2c_data'] = {
        'payment_type': 'payment_type',
        'payment_method_id': 'payment_id',
        'partner_tag': 'boxberry',
    }
    if not with_size:
        request['items'][0].pop('size', None)

    assert request['route_points'][0]['type'] == 'source'
    request['route_points'][0]['pickup_code'] = 'secret_code_1'
    return request


@pytest.fixture(name='get_default_c2c_request_v2')
def default_c2c_request_v2():
    return get_default_c2c_request_v2()


def get_default_headers_c2c():
    return {'Accept-Language': 'ru', 'X-Yandex-UID': 'user_id'}


# Direct fixture call workaround, see CARGODEV-1325
@pytest.fixture(name='get_default_params')
def _get_default_params_fixture():
    return _get_default_params()


def _get_default_params():
    def _wrapper(request_id=None, **kwargs):
        params = {}
        if request_id is None:
            params['request_id'] = get_default_idempotency_token()
        else:
            params['request_id'] = request_id
        return params

    return _wrapper


@pytest.fixture(name='create_default_cargo_c2c_order')
async def _create_default_cargo_c2c_order(
        taxi_cargo_claims,
        get_create_request_v2,
        get_default_idempotency_token,
        get_full_claim,
        default_estimation_result,
        mock_create_event,
):
    async def _wrapper(
            *,
            request=None,
            headers=None,
            payment_type='card',
            payment_method_id='card-123',
            is_phoenix=False,
            expected_meta_code=200,
            skip_mock_create_event=False,
            **kwargs,
    ):
        if not skip_mock_create_event:
            mock_create_event()
        if is_phoenix:
            corp_client_id = get_default_corp_client_id()
            payment_method_id = (
                'cargocorp:' + corp_client_id + ':card:' + YANDEX_UID + ':789'
            )
            payment_type = 'cargocorp'
        claim = copy.deepcopy(get_create_request_v2(**kwargs))
        claim['c2c_data'] = {
            'payment_type': payment_type,
            'payment_method_id': payment_method_id,
            'cargo_c2c_order_id': 'cargo_c2c_order_id',
        }
        if payment_method_id is None:
            del claim['c2c_data']['payment_method_id']
        for point in claim['route_points']:
            point['address']['description'] = 'some description'

        estimation_result = copy.deepcopy(
            default_estimation_result(
                cargo=kwargs['cargo'] if 'cargo' in kwargs else False,
            ),
        )
        estimation_result['offer']['offer_id'] = 'cargo-pricing/v1/123'
        if 'zone_id' in kwargs:
            estimation_result['zone_id'] = kwargs['zone_id']
        if 'point1_coords' in kwargs:
            claim['route_points'][0]['address']['coordinates'] = kwargs[
                'point1_coords'
            ]  # minsk
        c2c_claim_origin_info = {
            'origin': 'yandexgo',
            'user_agent': 'Mozilla',
            'customer_ip': '1.1.1.1',
        }

        request = {
            'claim': claim,
            'estimation_result': estimation_result,
            'c2c_claim_origin_info': c2c_claim_origin_info,
        }
        if headers is None:
            headers = {'Accept-Language': 'ru', 'X-Yandex-UID': 'user_id'}

        response = await taxi_cargo_claims.post(
            '/v2/claims/c2c/create',
            headers=headers,
            params={'request_id': get_default_idempotency_token},
            json=request,
        )
        assert response.status_code == expected_meta_code

        class Context:
            def __init__(self, response):
                self.claim_id = response.json().get('id', None)

        return Context(response)

    return _wrapper


@pytest.fixture(name='create_default_claim_v1')
async def _create_default_claim_v1(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_default_params,
):
    async def _wrapper(*, params=None, request=None, headers=None, **kwargs):
        if request is None:
            request = get_default_request(**kwargs)
        if headers is None:
            headers = get_default_headers(**kwargs)
        if params is None:
            params = get_default_params(**kwargs)

        response = await taxi_cargo_claims.post(
            'api/integration/v1/claims/create',
            params=params,
            json=request,
            headers=headers,
        )
        assert (
            response.status_code == 200
        ), 'DEFAULT_CREATE_REQUEST has bad request json. Fix it'

        class Context:
            def __init__(self, response):
                self.claim_id = response.json()['id']

        return Context(response)

    return _wrapper


@pytest.fixture(name='create_default_claim')
async def _create_default_claim(create_default_claim_v1):
    return await create_default_claim_v1()


@pytest.fixture
def get_default_create_query(get_default_idempotency_token):
    return {'request_id': get_default_idempotency_token}


@pytest.fixture(name='get_default_request')
def _get_default_request():
    def _wrapper(
            with_callback_url=False,
            skip_emergency_notify=False,
            without_email=False,
            with_phone_additional_code=False,
            no_return_point=False,
            skip_confirmation=False,
            optional_return=False,
            with_payment=False,
            skip_client_notify=False,
            additional_cargo_items=None,
            pro_courier=None,
            client_extra_requirement=None,
            with_brand_id=True,
            **kwargs,
    ):
        if additional_cargo_items is None:
            additional_cargo_items = []
        request = {
            'emergency_contact': {
                'name': 'emergency_name',
                'phone': '+79098887777',
            },
            # TODO: return with other additional info
            # 'recipient_info': {
            #     'is_individual': False,
            #     'name': 'Some Name',
            #     'address': 'Some address',
            #     'phone_number': '+71234567891',
            # },
            # 'shipment_info': {'details': 'some details',
            # 'name': 'some name'},
            # 'delivery_instructions': {
            #     'vehicle_requirements': 'some vehicle_requirements',
            # },
            'items': [
                {
                    'title': 'item title 1',
                    'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                    'cost_value': '10.40',
                    'cost_currency': 'RUB',
                    'weight': 10.2,
                    'quantity': 3,
                },
                {
                    'title': 'item title 2',
                    'size': {'length': 2.2, 'width': 5.0, 'height': 1.0},
                    'weight': 5,
                    'quantity': 1,
                    'cost_value': '0.20',
                    'cost_currency': 'RUB',
                },
            ] + additional_cargo_items,
            'comment': 'Очень полезный комментарий',
            'route_points': {
                'source': {
                    'address': {
                        'fullname': 'БЦ Аврора',
                        'coordinates': [37.5, 55.7],
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'Садовническая улица',
                        'building': '82',
                        'porch': '4',
                    },
                    'contact': {
                        'phone': '+71111111111',
                        'name': 'string',
                        'email': 'source@yandex.ru',
                    },
                    'skip_confirmation': skip_confirmation,
                },
                'destination': {
                    'address': {
                        'fullname': 'Свободы, 30',
                        'coordinates': [37.6, 55.6],
                        'country': 'Украина',
                        'city': 'Киев',
                        'street': 'Свободы',
                        'building': '30',
                        'porch': '2',
                        'floor': 12,
                        'flat': 87,
                        'sflat': '87B',
                        'door_code': '0к123',
                        'comment': 'other_comment',
                    },
                    'contact': {
                        'phone': '+72222222222',
                        'name': 'string',
                        'phone_additional_code': '123 45 678',
                    },
                    'skip_confirmation': skip_confirmation,
                },
                'return': {
                    'address': {
                        'fullname': 'Склад',
                        'coordinates': [37.8, 55.4],
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'МКАД',
                        'building': '50',
                    },
                    'contact': {
                        'phone': '+79999999999',
                        'name': 'string',
                        'email': 'return@yandex.ru',
                    },
                    'skip_confirmation': skip_confirmation,
                },
            },
            'client_requirements': {
                'taxi_class': 'cargo',
                'cargo_options': ['thermal_bag'],
            },
            'skip_emergency_notify': skip_emergency_notify,
            'custom_context': {'some_key1': 'some_value', 'some_key2': 123},
            'optional_return': optional_return,
            'skip_client_notify': skip_client_notify,
        }
        if with_callback_url:
            request['callback_url'] = 'https://www.example.com?'
        if without_email:
            for point_type, point in request['route_points'].items():
                if point_type == 'destination':
                    point['contact'].pop('email', None)
        if no_return_point:
            del request['route_points']['return']
        if with_payment:
            request['route_points']['destination']['payment_on_delivery'] = {
                'client_order_id': '1',
                'cost': '1.0000',
            }
        if pro_courier:
            request['client_requirements']['pro_courier'] = pro_courier
        if client_extra_requirement:
            request['client_requirements'][
                'extra_requirement'
            ] = client_extra_requirement
        if with_brand_id:
            request['custom_context']['brand_id'] = DEFAULT_BRAND_ID
        return request

    return _wrapper


def get_default_idempotency_token():
    return 'idempotency_token_1_default'


@pytest.fixture(name='get_default_idempotency_token')
def default_idempotency_token():
    return get_default_idempotency_token()


def get_default_corp_client_id():
    return '01234567890123456789012345678912'


@pytest.fixture(name='get_default_corp_client_id')
def default_corp_client_id():
    return get_default_corp_client_id()


def get_c2c_pricing_add_processing_event_request(
        is_create_accepted, calc_id, claim_id, corp_client_id=None,
):
    handler = 'v2/claims/c2c/create'
    req = {
        'entity_id': claim_id or matching.AnyString(),
        'events': [
            {'kind': 'create'},
            {
                'kind': 'calculation',
                'calc_id': calc_id,
                'price_for': 'client',
                'origin_uri': 'cargo_claims/{}/post'.format(handler),
                'calc_kind': 'offer',
            },
        ],
    }
    if corp_client_id:
        req['events'][1]['clients'] = [{'corp_client_id': corp_client_id}]

    return req


@pytest.fixture
def get_default_corp_claim_response(get_internal_claim_response):
    def _wrapper(claim_id, *, with_offer=False):
        result = {
            'emergency_contact': {
                'name': 'emergency_name',
                'phone': '+79098887777',
            },
            'skip_door_to_door': False,
            'skip_client_notify': False,
            'skip_emergency_notify': False,
            'optional_return': False,
            'comment': 'Очень полезный комментарий',
            'available_cancel_state': 'free',
        }

        result.update(
            get_internal_claim_response(claim_id, with_offer=with_offer),
        )
        result.pop('user_locale')
        result['emergency_contact']['phone'] = result['emergency_contact'][
            'personal_phone_id'
        ][:-3]
        result['emergency_contact'].pop('personal_phone_id')
        for point_type in result['route_points']:
            result['route_points'][point_type]['contact']['phone'] = result[
                'route_points'
            ][point_type]['contact']['personal_phone_id'][:-3]
            result['route_points'][point_type]['contact'].pop(
                'personal_phone_id',
            )

            if point_type != 'destination':
                result['route_points'][point_type]['contact']['email'] = (
                    result['route_points'][point_type]['contact'][
                        'personal_email_id'
                    ][:-3]
                )
                result['route_points'][point_type]['contact'].pop(
                    'personal_email_id',
                )
        result['items'][0].pop('id')
        result['items'][1].pop('id')
        return result

    return _wrapper


@pytest.fixture
def get_internal_claim_response():
    def _wrapper(claim_id, *, with_offer=False, with_custom_context=False):
        response = {
            'id': claim_id,
            'version': 1,
            'user_request_revision': '1',
            'status': 'new',
            'corp_client_id': '01234567890123456789012345678912',
            'emergency_contact': {
                'name': 'emergency_name',
                'personal_phone_id': '+79098887777_id',
            },
            'skip_door_to_door': False,
            'skip_client_notify': False,
            'skip_emergency_notify': False,
            'skip_act': False,
            'optional_return': False,
            'comment': 'Очень полезный комментарий',
            'available_cancel_state': 'free',
            'pricing': {},
            'user_locale': 'en',
            'items': [
                {
                    'title': 'item title 1',
                    'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                    'weight': 10.2,
                    'cost_value': '10.40',
                    'cost_currency': 'RUB',
                    'quantity': 3,
                    'id': 1,
                },
                {
                    'title': 'item title 2',
                    'size': {'length': 2.2, 'width': 5.0, 'height': 1.0},
                    'weight': 5.0,
                    'quantity': 1,
                    'id': 2,
                    'cost_value': '0.20',
                    'cost_currency': 'RUB',
                },
            ],
            'route_points': {
                'source': {
                    'address': {
                        'fullname': 'БЦ Аврора',
                        'coordinates': [37.5, 55.7],
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'Садовническая улица',
                        'building': '82',
                        'porch': '4',
                    },
                    'contact': {
                        'personal_phone_id': '+71111111111_id',
                        'personal_email_id': 'source@yandex.ru_id',
                        'name': 'string',
                    },
                    'skip_confirmation': False,
                },
                'destination': {
                    'address': {
                        'fullname': 'Свободы, 30',
                        'coordinates': [37.6, 55.6],
                        'country': 'Украина',
                        'city': 'Киев',
                        'street': 'Свободы',
                        'building': '30',
                        'porch': '2',
                        'floor': 12,
                        'flat': 87,
                        'sfloor': '12',
                        'sflat': '87B',
                        'door_code': '0к123',
                        'comment': 'other_comment',
                    },
                    'contact': {
                        'personal_phone_id': '+72222222222_id',
                        'name': 'string',
                        'phone_additional_code': '123 45 678',
                    },
                    'skip_confirmation': False,
                },
                'return': {
                    'address': {
                        'fullname': 'Склад',
                        'coordinates': [37.8, 55.4],
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'МКАД',
                        'building': '50',
                    },
                    'contact': {
                        'personal_phone_id': '+79999999999_id',
                        'personal_email_id': 'return@yandex.ru_id',
                        'name': 'string',
                    },
                    'skip_confirmation': False,
                },
            },
            'client_requirements': {
                'taxi_class': 'cargo',
                'cargo_options': ['thermal_bag'],
            },
        }

        if with_custom_context:
            response['custom_context'] = {
                'some_key1': 'some_value',
                'some_key2': 123,
                'brand_id': DEFAULT_BRAND_ID,
            }

        if with_offer:
            response['pricing'] = {
                'currency': 'RUB',
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '1198.8012',
                    'price_raw': 999,
                },
            }
            response['taxi_offer'] = {
                'offer_id': 'taxi_offer_id_1',
                'price': '1198.8012',
                'price_raw': 999,
            }
            response['matched_cars'] = [
                {
                    'cargo_loaders': 2,
                    'cargo_type': 'lcv_m',
                    'taxi_class': 'cargo',
                },
            ]
        return response

    return _wrapper


def get_default_driver_auth_headers():
    return {
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'en',
    }


@pytest.fixture(name='get_default_driver_auth_headers')
def default_driver_auth_headers():
    return get_default_driver_auth_headers()


def get_taxi_order_fail_request(taxi_order_id=None):
    if taxi_order_id is None:
        taxi_order_id = 'taxi_order_id_1'
    return {
        'taxi_order_id': taxi_order_id,
        'reason': 'some_reason',
        'lookup_version': 1,
    }


def get_lookup_drafted_request(taxi_order_id=None):
    if taxi_order_id is None:
        taxi_order_id = 'taxi_order_id_1'
    return {'taxi_order_id': taxi_order_id, 'taxi_user_id': 'taxi_user_id_1'}


def get_finish_estimate_request_offer(offer_id, cargo_pricing_flow):
    price = '999.0010'
    if offer_id == NO_PRICING_CALC_ID:
        price = '0'
    elif cargo_pricing_flow:
        offer_id = 'cargo-pricing/v1/' + offer_id
    return {
        'offer_id': offer_id,
        'price_raw': int(float(price)),
        'price': price,
        'currency_code': 'RUB',
    }


@pytest.fixture(name='get_finish_estimate_request')
def _get_finish_estimate_request():
    def _wrapper(
            taxi_class='cargo',
            cargo_type='lcv_m',
            cargo_loaders=2,
            door_to_door=False,
            cargo_pricing_flow=False,
            fake_middle_points=False,
            finish_estimate_pro_courier_requirements=False,
            finish_estimate_extra_requirement=None,
            offer_id='taxi_offer_id_1',
            **kwargs,
    ):
        requirements = {}
        if door_to_door:
            requirements['door_to_door'] = True
        if cargo_type:
            requirements['cargo_type'] = cargo_type
        if cargo_loaders:
            requirements['cargo_loaders'] = cargo_loaders
        if fake_middle_points:
            requirements['cargo_points'] = [2, 2]
            requirements['cargo_points_field'] = 'fake_middle_point_express'
        if finish_estimate_pro_courier_requirements:
            requirements['pro_courier'] = True
        if finish_estimate_extra_requirement:
            requirements[
                'extra_requirement'
            ] = finish_estimate_extra_requirement
        return {
            'cars': [
                {
                    'taxi_class': taxi_class,
                    'cargo_type': cargo_type,
                    'taxi_requirements': requirements,
                    'items': [{'id': 1, 'quantity': 1}],
                },
            ],
            'offer': get_finish_estimate_request_offer(
                offer_id, cargo_pricing_flow,
            ),
            'currency': 'RUB',
            'zone_id': 'moscow',
            'total_distance_meters': 2000,
        }

    return _wrapper


def get_order_complete_request(taxi_order_id='taxi_order_id_1'):
    return {
        'taxi_order_id': taxi_order_id,
        'reason': 'reason',
        'lookup_version': 1,
    }


@pytest.fixture
async def create_claim_with_performer(taxi_cargo_claims, state_controller):
    return await state_controller.apply(target_status='performer_found')


@pytest.fixture
def create_default_documents(taxi_cargo_claims, pgsql, mds_s3_storage):
    def _wrapper(claim_id):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_claims.documents (
            claim_id,
            claim_uuid,
            document_type,
            mds_path,
            claim_status,
            driver_id,
            park_id
            )
            VALUES ('{claim_id}',
                    '{claim_id}', 'act',
                    'documents/someuuid',
                    'new',
                    'driver_id1',
                    'park_id1'
                    );
        """,
        )
        mds_s3_storage.put_object(
            '/mds-s3/documents/someuuid', b'PDF FILE MOCK',
        )

    return _wrapper


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


@pytest.fixture
def check_support_audit_last(taxi_cargo_claims):
    async def _wrapper(
            old_status,
            new_status,
            claim_id,
            expected_comment='support_comment',
            expected_ticket='TICKET-100',
    ):
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/full', params={'claim_id': claim_id},
        )
        assert response.status_code == 200
        json = response.json()

        history_audit = json['history']
        audit_found = False
        for audit in history_audit:
            if audit.get('comment', None) != expected_comment:
                continue
            if audit.get('ticket', None) != expected_ticket:
                continue
            if audit.get('new_status', None) != new_status:
                continue
            if audit.get('old_status', None) != old_status:
                continue
            audit_found = True
            break

        assert audit_found, f'Not found in audit: {history_audit}'

    return _wrapper


@pytest.fixture
async def get_claim_status(taxi_cargo_claims):
    async def wrapper(cargo_ref_id: str) -> str:
        response = await taxi_cargo_claims.get(
            'v1/claims/cut', params={'claim_id': cargo_ref_id},
        )
        assert response.status_code == 200
        return response.json()['status']

    return wrapper


# fix flaps with extra 0 in floating point string representation
@pytest.fixture
async def remove_dates():
    def _wrapper(modified_dict, with_due=False):
        date_fields = ['updated_ts', 'created_ts', 'revision']
        if with_due:
            date_fields.append('due')

        for key in date_fields:
            modified_dict.pop(key, None)

    return _wrapper


@pytest.fixture(autouse=True)
async def fix_sync_pk(pgsql):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute('ALTER SEQUENCE cargo_claims.points_id_seq RESTART 1000;')


@pytest.fixture
async def state_new_claim_with_callback_url(
        claim_creator, get_default_request,
):  # pylint: disable=invalid-name
    callback = 'https://www.example.com?'

    request_data = get_default_request()
    request_data['callback_properties'] = {'callback_url': callback}

    response = await claim_creator(request=request_data)
    assert response.status_code == 200

    class State:
        def __init__(self, response):
            self.callback_url = callback
            self.claim_id = response.json()['id']

    return State(response)


@pytest.fixture(name='now_plus_30min')
async def _now_plus_30min(now):
    return now + datetime.timedelta(minutes=30)


@pytest.fixture(name='to_iso8601')
def _to_iso8601():
    def _wrapper(stamp, timezone='Europe/Moscow'):
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=pytz.utc)
        stamp = stamp.astimezone(pytz.timezone(timezone))
        return stamp.strftime(ISO8601_FORMAT)

    return _wrapper


@pytest.fixture(name='from_iso8601')
def _from_iso8601():
    def _wrapper(timestring):
        stamp = dateutil.parser.parse(timestring)
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=pytz.utc)
        return stamp.astimezone(pytz.utc).replace(tzinfo=None)

    return _wrapper


@pytest.fixture(name='close_datetimes')
def _close_datetimes():
    def _wrapper(ts1, ts2):
        return abs((ts1 - ts2).total_seconds()) < 1.000001

    return _wrapper


@pytest.fixture(name='state_new_claim_with_due')
async def _state_new_claim_with_due(
        claim_creator, get_default_request, now_plus_30min, to_iso8601,
):  # pylint: disable=invalid-name
    request_data = get_default_request()
    request_data['due'] = to_iso8601(now_plus_30min)

    response = await claim_creator(request=request_data)
    assert response.status_code == 200

    class State:
        def __init__(self, response):
            self.due = now_plus_30min
            self.claim_id = response.json()['id']
            self.version = response.json()['version']

    return State(response)


@pytest.fixture
async def get_claim(taxi_cargo_claims, get_default_headers):
    async def _wrapper(claim_id):
        response = await taxi_cargo_claims.post(
            '/api/integration/v1/claims/info',
            params={'claim_id': claim_id},
            headers=get_default_headers(),
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture
async def get_claim_v2(taxi_cargo_claims):
    async def wrapper(claim_id):
        response = await taxi_cargo_claims.get(
            'v2/claims/full', params={'claim_id': claim_id},
        )

        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture
def get_claim_inner_v2(taxi_cargo_claims, get_default_headers):
    async def _wrapper(claim_id):
        response = await taxi_cargo_claims.get(
            'v2/claims/full',
            params={'claim_id': claim_id},
            headers=get_default_headers(),
        )
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(autouse=True)
def mocker_archive_get_order_proc(order_archive_mock):
    def wrapper(json):
        if json is not None:
            order_archive_mock.set_order_proc(json)

        return order_archive_mock.order_proc_retrieve

    return wrapper


@pytest.fixture(autouse=True)
def mock_archive_api(mockserver):
    @mockserver.json_handler('/archive-api/archive/order')
    def _order(request):
        response = {
            'doc': {'payment_tech': {'without_vat_to_pay': {'ride': 1230000}}},
        }
        return mockserver.make_response(bson.BSON.encode(response), status=200)


@pytest.fixture
def mock_yt_queries(mockserver):
    def _impl(queries_list):
        @mockserver.json_handler('/archive-api/v1/yt/select_rows')
        def _mock_archive_api(request):
            for item in queries_list:
                if request.json == item['request']:
                    return item['response']
            assert False, str(request.json) + ' not found'
            return None

        return _mock_archive_api

    return _impl


@pytest.fixture
def state_indirect(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
async def get_current_claim_point(taxi_cargo_claims):
    async def wrapper(cargo_ref_id: str):
        response = await taxi_cargo_claims.get(
            'v2/claims/full', params={'claim_id': cargo_ref_id},
        )
        assert response.status_code == 200
        return response.json().get('current_point_id', None)

    return wrapper


@pytest.fixture
async def get_full_claim(taxi_cargo_claims):
    async def wrapper(cargo_ref_id: str):
        response = await taxi_cargo_claims.get(
            'v2/claims/full', params={'claim_id': cargo_ref_id},
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture
def get_create_request_v2():
    def _wrapper(**kwargs):
        from . import utils_v2
        return utils_v2.get_create_request(**kwargs)

    return _wrapper


@pytest.fixture(name='default_estimation_result')
def _default_estimation_result(**kwargs):
    def _wrapper(*, cargo=False):
        result = {
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'zone_id': 'moscow',
            'eta': 30,
            'taxi_class': 'express',
            'requirements': {'door_to_door': True},
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$ $CURRENCY$',
                'text': 'руб.',
            },
        }
        if cargo:
            result['taxi_class'] = 'cargo'
            result['requirements'] = {
                'cargo_type': 'lcv_m',
                'cargo_loaders': 2,
                'door_to_door': True,
                'thermobag_covid': True,
                'claim_taxi_requirements_str': 'taxi_req',
                'claim_taxi_requirements_bool': True,
                'claim_taxi_requirements_num': 2,
            }
        return result

    return _wrapper


@pytest.fixture(name='get_default_c2c_request_v2_full')
def _get_default_c2c_request_v2_full(default_estimation_result):
    def _wrapper(*, with_size=True, cargo=False, **kwargs):
        return {
            'claim': get_default_c2c_request_v2(with_size, **kwargs),
            'estimation_result': default_estimation_result(
                cargo=cargo, **kwargs,
            ),
        }

    return _wrapper


@pytest.fixture(name='mock_nearestzone', autouse=True)
def _mock_nearestzone(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/nearestzone')
    def mock(request):
        return {'nearest_zone': 'moscow'}

    return mock


@pytest.fixture
def clear_event_times():
    def _wrapper(json):
        json.pop('updated_ts', None)
        json.pop('created_ts', None)
        json.pop('revision', None)
        json.get('claim', {}).pop('updated_ts', None)
        json.get('claim', {}).pop('created_ts', None)
        json.get('claim', {}).pop('revision', None)
        for audit in json.get('history', {}):
            audit.pop('event_time', None)

    return _wrapper


def get_expected_point_values(request_v2):
    def make_id(string):
        return string + '_id' if string is not None else None

    points = request_v2['route_points']
    values = []
    for x in sorted(points, key=lambda x: x['visit_order']):
        value = {
            'type': x['type'],
            'visit_order': x['visit_order'],
            'skip_confirmation': x.get('skip_confirmation', False),
            'contact': {
                'personal_phone_id': make_id(x['contact'].get('phone')),
                'personal_email_id': make_id(x['contact'].get('email')),
            },
            'address': {
                'fullname': x['address']['fullname'],
                'uri': x['address'].get('uri'),
            },
        }
        values.append(value)

    return values


def get_expected_item_values(request_v2):
    items = request_v2['items']

    values = []
    for item in items:
        value = {'extra_id': item.get('extra_id')}
        values.append(value)

    return values


def check_contains_in_dict(inner, outer):
    for key, value in inner.items():
        if isinstance(value, dict):
            check_contains_in_dict(value, outer[key])
        elif value is not None:
            assert value == outer[key], f'value {value} not in {outer[key]}'


@pytest.fixture
def check_v2_response():
    def _wrapper(*, request, response):
        route_points = response['route_points']
        expected_point_values = get_expected_point_values(request)

        assert len(route_points) == len(expected_point_values)
        for index, _ in enumerate(route_points):
            check_contains_in_dict(
                expected_point_values[index], route_points[index],
            )

        items = response['items']
        expected_item_values = get_expected_item_values(request)

        assert len(items) == len(expected_item_values)
        for index, _ in enumerate(items):
            check_contains_in_dict(expected_item_values[index], items[index])

    return _wrapper


@pytest.fixture(name='claims_creator_v1')
def _claims_creator_v1(taxi_cargo_claims, create_default_claim_v1):
    async def _wrapper(**kwargs):
        return await create_default_claim_v1(**kwargs)

    return _wrapper


@pytest.fixture(name='claims_creator_v2_cargo_c2c')
def _claims_creator_v2_cargo_c2c(create_default_cargo_c2c_order):
    async def _wrapper(**kwargs):
        return await create_default_cargo_c2c_order(**kwargs)

    return _wrapper


@pytest.fixture
async def claims_creator(
        claims_creator_v1, claims_creator_v2, claims_creator_v2_cargo_c2c,
):
    return {
        'v1': claims_creator_v1,
        'v2': claims_creator_v2,
        'v2_cargo_c2c': claims_creator_v2_cargo_c2c,
    }


@pytest.fixture
def state_controller_fixtures(
        taxi_cargo_claims,
        stq_runner,
        claims_creator,
        get_finish_estimate_request,
        get_default_headers,
        set_last_status_change_ts,
        build_segment_update_request,
        get_segment_id,
        create_segment_for_claim,
        get_claim,
        arrive_at_point,
        exchange_init,
        exchange_return,
        exchange_confirm,
):
    class Fixtures:
        def __init__(self):
            self.taxi_cargo_claims = taxi_cargo_claims
            self.stq_runner = stq_runner
            self.claims_creator = claims_creator
            self.get_finish_estimate_request = get_finish_estimate_request
            self.get_default_headers = get_default_headers
            self.set_last_status_change_ts = set_last_status_change_ts
            self.build_segment_update_request = build_segment_update_request
            self.get_segment_id = get_segment_id
            self.create_segment_for_claim = create_segment_for_claim
            self.get_claim = get_claim
            self.segment_arrive_at_point = arrive_at_point
            self.segment_exchange_init = exchange_init
            self.segment_exchange_return = exchange_return
            self.segment_exchange_confirm = exchange_confirm

    return Fixtures()


@pytest.fixture
def check_taxi_order_change(pgsql):
    def _wrapper(
            *, claim_uuid, taxi_order_id=None, reason=None, new_status=None,
    ):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""
            SELECT taxi_order_id, reason, new_claim_status
            FROM cargo_claims.taxi_order_changes
            WHERE claim_uuid = '{claim_uuid}'
            """,
        )
        rows = cursor.fetchall()
        assert rows
        for pg_taxi_order_id, pg_reason, pg_new_status in rows:
            if reason is not None:
                if pg_reason != reason:
                    continue
            if new_status is not None:
                if pg_new_status != new_status:
                    continue
            if taxi_order_id is not None:
                if pg_taxi_order_id != taxi_order_id:
                    continue
            return

        assert False, f'No such status for "{reason}" "{new_status}"'

    return _wrapper


@pytest.fixture
async def get_pickup_codes(pgsql):
    def _wrapper():
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f'SELECT pickup_code, pickup_code_receipt_timestamp '
            f' FROM cargo_claims.claim_points',
        )
        return {
            row[0]: row[1] for row in cursor.fetchall() if row[0] is not None
        }

    return _wrapper


@pytest.fixture(autouse=True)
def cargo_misc(mockserver):
    @mockserver.json_handler(
        '/cargo-misc/api/b2b/cargo-misc/v1/claims/comments/default',
    )
    def _default_comment(request, *args, **kwargs):
        return {
            'id': 'some id',
            'name': 'some comment name',
            'comment': 'some comment',
            'tariff': 'cargo',
        }


@pytest.fixture
async def set_last_status_change_ts(pgsql, now):
    def _wrapper():
        cursor = pgsql['cargo_claims'].conn.cursor()
        timestamp = now.replace(tzinfo=datetime.timezone.utc).isoformat()
        cursor.execute(
            f"""
            UPDATE cargo_claims.claims
            SET last_status_change_ts=\'{timestamp}\'
        """,
        )
        cursor.execute(
            f"""
            UPDATE cargo_claims.claim_points
            SET last_status_change_ts=\'{timestamp}\'
        """,
        )

    return _wrapper


@pytest.fixture
async def check_zone_id(pgsql):
    def _wrapper(*, claim_id, zone_id='moscow'):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""SELECT zone_id FROM cargo_claims.claims
                WHERE uuid_id= '{claim_id}'""",
        )
        assert zone_id == list(cursor)[0][0]

    return _wrapper


@pytest.fixture
async def get_sharing_keys(pgsql):
    def _wrapper(*, claim_uuid):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f'SELECT sharing_key '
            f'FROM cargo_claims.claim_points '
            f'WHERE claim_uuid = \'{claim_uuid}\' '
            f'ORDER BY visit_order',
        )
        return [row[0] for row in cursor.fetchall()]

    return _wrapper


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(
            pytest.mark.experiments3(filename='exp3_esignature.json'),
        )
        item.add_marker(pytest.mark.geoareas(filename='geoareas_moscow.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture
async def set_up_create_experiment(taxi_cargo_claims, experiments3):
    async def _wrapper(
            *,
            experiment: str,
            matched: dict,
            not_matched: dict,
            corp_client_id: str = 'unknown',
            zone_id: str = 'unknown',
            recipient_phone: str = None,
    ):
        predicates_by_corp = [
            {
                'init': {
                    'set': [corp_client_id],
                    'arg_name': 'corp_client_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        ]
        if recipient_phone:
            predicates_by_corp.append(
                {
                    'init': {
                        'set_elem_type': 'string',
                        'arg_name': 'recipients_phones',
                        'value': recipient_phone,
                    },
                    'type': 'contains',
                },
            )
        predicates_by_zone = [
            {
                'init': {
                    'set': [zone_id],
                    'arg_name': 'zone_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        ]

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=experiment,
            consumers=['cargo-claims/create-claim'],
            clauses=[
                {
                    'title': 'corp_client_id',
                    'predicate': {
                        'init': {'predicates': predicates_by_corp},
                        'type': 'all_of',
                    },
                    'value': matched,
                },
                {
                    'title': 'corp_client_id',
                    'predicate': {
                        'init': {'predicates': predicates_by_zone},
                        'type': 'all_of',
                    },
                    'value': matched,
                },
            ],
            default_value=not_matched,
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture(name='exp_cargo_claims_post_payment_clients')
async def _exp_cargo_claims_post_payment_clients(
        experiments3, taxi_cargo_claims,
):
    async def wrapper(*, enabled=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_post_payment_clients',
            consumers=[
                'cargo-claims/check-postpayment',
                'cargo-claims/postpayment-setting',
            ],
            clauses=[],
            default_value={
                'enabled': enabled,
                'logistic_contract_required': False,
            },
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


@pytest.fixture(name='set_up_tariff_substitution_exp')
def _set_up_tariff_substitution_exp(taxi_cargo_claims, experiments3):
    async def _wrapper(
            *,
            enabled: bool = True,
            corp_client_id: str = 'unknown',
            zone_id: str = 'unknown',
    ):
        predicates = []
        predicates.append(
            {
                'init': {
                    'set': [corp_client_id],
                    'arg_name': 'corp_client_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        )
        predicates.append(
            {
                'init': {
                    'set': [zone_id],
                    'arg_name': 'zone_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        )

        matched_delayed_express = {
            'extended_tariffs': {
                'extra_classes': ['cargo', 'express'],
                'delayed_classes': [
                    {
                        'taxi_classes': ['express'],
                        'delay': {'since_lookup': 100, 'since_due': -250},
                    },
                ],
            },
        }
        matched_delayed_courier = {
            'extended_tariffs': {
                'extra_classes': ['cargo', 'courier'],
                'delayed_classes': [
                    {
                        'taxi_classes': ['courier'],
                        'delay': {'since_lookup': 200, 'since_due': -150},
                    },
                ],
            },
        }

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': enabled},
            name='cargo_delayed_express',
            consumers=['cargo-claims/segment-info'],
            clauses=[
                {
                    'title': 'title',
                    'predicate': predicate,
                    'value': {'delayed_express': matched_delayed_express},
                }
                for predicate in predicates
            ],
            default_value={},
            merge_values_by=_CARGO_EXTENDED_LOOKUP_MERGE_TAG,
        )
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': enabled},
            name='cargo_delayed_courier',
            consumers=['cargo-claims/segment-info'],
            clauses=[
                {
                    'title': 'title',
                    'predicate': predicate,
                    'value': {'delayed_courier': matched_delayed_courier},
                }
                for predicate in predicates
            ],
            default_value={},
            merge_values_by=_CARGO_EXTENDED_LOOKUP_MERGE_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture(name='set_tariffs_exp_with_fallback')
def _set_tariffs_exp_with_fallback(taxi_cargo_claims, experiments3):
    # Fallback with ignorable special requirements
    async def _wrapper(*, enabled: bool = True):
        matched_delayed_express = {
            'extended_tariffs': {
                'extra_classes': ['courier', 'express'],
                'delayed_classes': [
                    {
                        'taxi_classes': ['express'],
                        'delay': {'since_lookup': 600, 'since_due': -300},
                    },
                ],
            },
        }
        matched_ignored_thermobag = {
            'ignorable_special_requirements': [
                {
                    'requirements': ['thermobag_confirmed'],
                    'taxi_classes': ['courier'],
                    'delay': {'since_lookup': 60, 'since_due': -600},
                },
                {
                    'requirements': ['thermobag_confirmed'],
                    'taxi_classes': ['express'],
                    'delay': {'since_lookup': 600, 'since_due': -300},
                },
            ],
        }

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': enabled},
            name='cargo_delayed_express',
            consumers=['cargo-claims/segment-info'],
            clauses=[],
            default_value={'delayed_express': matched_delayed_express},
            merge_values_by=_CARGO_EXTENDED_LOOKUP_MERGE_TAG,
        )
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': enabled},
            name='cargo_ignored_thermobag',
            consumers=['cargo-claims/segment-info'],
            clauses=[],
            default_value={'ignored_thermobad': matched_ignored_thermobag},
            merge_values_by=_CARGO_EXTENDED_LOOKUP_MERGE_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture
def set_up_allow_batch_exp(experiments3):
    def _wrapper(
            *,
            corp_client_id: str = 'unknown',
            zone_id: str = 'unknown',
            source_point: list = None,
            recipient_phone: str = None,
    ):
        predicates = []
        predicates.append(
            {
                'init': {
                    'set': [corp_client_id],
                    'arg_name': 'corp_client_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        )
        predicates.append(
            {
                'init': {
                    'set': [zone_id],
                    'arg_name': 'zone_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        )
        if source_point is not None:
            delta = 0.000001
            square = []
            square.append([source_point[0] - delta, source_point[1] - delta])
            square.append([source_point[0] + delta, source_point[1] - delta])
            square.append([source_point[0] + delta, source_point[1] + delta])
            square.append([source_point[0] - delta, source_point[1] + delta])

            predicates.append(
                {
                    'type': 'falls_inside',
                    'init': {
                        'arg_name': 'source_point',
                        'arg_type': 'linear_ring',
                        'value': square,
                    },
                },
            )

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_segment_creator',
            consumers=['cargo-claims/segment-creator'],
            clauses=[
                {
                    'title': 'title',
                    'predicate': predicate,
                    'value': {'allow_batch': True},
                }
                for predicate in predicates
            ],
            default_value={'allow_batch': False},
        )

    return _wrapper


@pytest.fixture
async def get_db_segment_ids(taxi_cargo_claims, run_journal_events_mover):
    async def _wrapper():
        # Move events from buffer to journal
        await run_journal_events_mover()

        response = await taxi_cargo_claims.post('v1/segments/journal', json={})
        assert response.status_code == 200

        result_segments: list = []
        for ent in response.json()['entries']:
            if ent['segment_id'] not in result_segments:
                result_segments.append(ent['segment_id'])
        return result_segments

    return _wrapper


@pytest.fixture
def get_segment_id(get_db_segment_ids):
    async def _wrapper():
        segment_ids = await get_db_segment_ids()

        return segment_ids[0]

    return _wrapper


@pytest.fixture
def get_segment(taxi_cargo_claims):
    async def wrapper(segment_id):
        response = await taxi_cargo_claims.post(
            '/v1/segments/info', params={'segment_id': segment_id},
        )
        assert response.status_code == 200

        return response.json()

    return wrapper


@pytest.fixture
async def get_claim_update_datetime(pgsql):
    def _wrapper():
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""SELECT last_status_change_ts FROM cargo_claims.claims""",
        )
        return cursor.fetchall()[0][0]

    return _wrapper


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_claims, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await taxi_cargo_claims.run_task(task_name)
        args = await task_result.wait_call()
        assert not task_result.has_calls

        return args['result']

    return _wrapper


@pytest.fixture(name='run_processing_events')
def _run_processing_events(
        run_task_once, pgsql, stq_runner, mockserver, taxi_cargo_claims,
):
    async def _wrapper(should_set_stq=True, expect_fail=False, limit=100):
        await taxi_cargo_claims.tests_control(reset_metrics=True)

        @mockserver.json_handler(
            '/stq-agent/queues/api/add/cargo_claims_processing_events/bulk',
        )
        async def _mock_call(request):
            data = request.json
            response = {'tasks': []}
            for task in data['tasks']:
                if should_set_stq:
                    await stq_runner.cargo_claims_processing_events.call(
                        task_id=task['task_id'],
                        kwargs=task['kwargs'],
                        expect_fail=expect_fail,
                    )
                    if expect_fail:
                        response['tasks'].append(
                            {
                                'task_id': task['task_id'],
                                'add_result': {
                                    'code': 500,
                                    'description': 'task failed',
                                },
                            },
                        )
                    else:
                        response['tasks'].append(
                            {
                                'task_id': task['task_id'],
                                'add_result': {'code': 200},
                            },
                        )
            return response

        return await run_task_once('cargo-claims-processing-events')

    return _wrapper


@pytest.fixture(name='run_worker_stats_monitor')
def _run_worker_stats_monitor(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-claims-worker-stats-monitor')

    return _wrapper


@pytest.fixture(name='run_corp_billing')
def _run_corp_billing(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-claims-corp-billing')

    return _wrapper


@pytest.fixture(name='run_cargo_pricing_handler')
def _run_cargo_pricing_handler(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-claims-cargo-pricing-handler')

    return _wrapper


@pytest.fixture(name='run_journal_events_mover')
def _run_journal_events_mover(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-claims-journal-events-mover')

    return _wrapper


def _get_shifted_timestamp(now, **kwargs):
    timestamp = now + datetime.timedelta(**kwargs)
    return timestamp.strftime(format='%Y-%m-%dT%H:%M:%SZ')


def _items_cost(claim_point_id, request):
    cost = 0.0
    for item in request['items']:
        if item['droppof_point'] == claim_point_id:
            cost += float(item['cost_value']) * item['quantity']
    return str(cost)


def _add_payment_on_delivery(
        request,
        *,
        payment_method: str = None,
        external_payment_id: str = None,
        external_postpayment_flow: bool = False,
        post_payment_nds: str = 'vat10',
        post_payment_mark=None,
        post_payment_item_type: str = None,
        **kwargs,
):
    if payment_method is None:
        return

    for item in request['items']:
        item['fiscalization'] = {
            'article': 'article of ' + item['title'],
            'vat_code_str': post_payment_nds,
            'supplier_inn': '0123456788',
        }
        if post_payment_mark:
            item['fiscalization']['mark'] = post_payment_mark
        if post_payment_item_type:
            item['fiscalization']['item_type'] = post_payment_item_type

    for point in request['route_points']:
        if point['type'] == 'destination':
            if external_postpayment_flow:
                point['payment_on_delivery'] = {
                    'payment_method': payment_method,
                    'external_payment_id': str(uuid.uuid4()),
                }
            else:
                point['payment_on_delivery'] = {
                    'payment_method': payment_method,
                    'customer': {
                        'email': 'customer@yandex.ru',
                        'phone': '+79999999991',
                    },
                }
                if external_payment_id is not None:
                    point['payment_on_delivery'][
                        'external_payment_id'
                    ] = external_payment_id


@pytest.fixture(name='build_create_request')
def _build_create_request(get_create_request_v2, get_default_request):
    def _wrapper(
            pickup_code: str = None,
            drop_item_size: bool = False,
            due: str = None,
            lookup_ttl: str = None,
            with_time_intervals: bool = False,
            use_create_v2: bool = False,
            now: datetime.datetime = None,
            claim_kind: str = None,
            client_req_taxi_classes: tp.List[str] = None,
            skip_client_requirements: bool = False,
            custom_context: dict = None,
            optional_return: bool = None,
            payment_method: str = None,
            features: tp.List[str] = None,
            multipoints: bool = True,
            with_return: bool = True,
            assign_robot: bool = False,
            same_day_data: dict = None,
            **kwargs,
    ):
        if payment_method or pickup_code or with_time_intervals:
            use_create_v2 = True
        if use_create_v2:
            request = copy.deepcopy(
                get_create_request_v2(
                    multipoints=multipoints, with_return=with_return, **kwargs,
                ),
            )
        else:
            request = copy.deepcopy(get_default_request(**kwargs))

        _add_payment_on_delivery(
            request, payment_method=payment_method, **kwargs,
        )

        if now is None:
            now = datetime.datetime.utcnow()

        if pickup_code:
            request['route_points'][0]['pickup_code'] = pickup_code

        if drop_item_size:
            for item in request['items']:
                item.pop('size', None)
                item.pop('weight', None)

            request['client_requirements'] = {
                'taxi_class': 'express',
                'door_to_door': True,
            }

        if due:
            request['due'] = due

        if lookup_ttl:
            request['lookup_ttl'] = lookup_ttl

        if with_time_intervals:
            request['route_points'][0]['time_intervals'] = [
                {
                    'type': 'strict_match',
                    'from': _get_shifted_timestamp(now, minutes=10),
                    'to': _get_shifted_timestamp(now, minutes=25),
                },
            ]
            request['route_points'][1]['time_intervals'] = [
                {
                    'type': 'strict_match',
                    'from': _get_shifted_timestamp(now, minutes=30),
                    'to': _get_shifted_timestamp(now, minutes=35),
                },
                {
                    'type': 'perfect_match',
                    'from': _get_shifted_timestamp(now, minutes=20),
                    'to': _get_shifted_timestamp(now, minutes=45),
                },
            ]

        request['requirements'] = {}
        request['requirements']['soft_requirements'] = [
            {
                'type': 'performer_group',
                'logistic_group': 'lavka',
                'performers_restriction_type': 'group_only',
            },
        ]

        if claim_kind:
            request['claim_kind'] = claim_kind

        if skip_client_requirements:
            request.pop('client_requirements', None)
        else:
            if client_req_taxi_classes:
                request['client_requirements'][
                    'taxi_classes'
                ] = client_req_taxi_classes
            if assign_robot:
                request['client_requirements']['assign_robot'] = assign_robot

        if custom_context is not None:
            request['custom_context'] = custom_context
        else:
            request.pop('custom_context', None)

        if optional_return is not None:
            request['optional_return'] = optional_return

        if features:
            request['features'] = features

        if same_day_data is not None:
            request['same_day_data'] = same_day_data

        return request, 'v2' if use_create_v2 else None

    return _wrapper


@pytest.fixture(name='create_claim_for_segment')
def _create_claim_for_segment(
        state_controller,
        get_default_corp_client_id,
        build_create_request,
        mock_cargo_corp,
):
    async def _wrapper(
            status: str = 'accepted',
            claim_index: int = 0,
            is_phoenix: bool = False,
            **kwargs,
    ):

        handlers_context = state_controller.handlers(claim_index=claim_index)
        create = handlers_context.create

        create.request, create_version = build_create_request(**kwargs)
        if create_version is not None:
            state_controller.use_create_version(
                create_version, claim_index=claim_index,
            )

        create.params = {'request_id': f'idempotency_token_{claim_index}'}
        create.headers = _get_default_headers()()
        create.headers['User-Agent'] = 'Yandex'
        if is_phoenix:
            mock_cargo_corp.is_cargo_corp_down = False
            create.headers['X-B2B-Client-Storage'] = 'cargo'

        state_controller.set_options(**kwargs, claim_index=claim_index)
        claim = await state_controller.apply(
            target_status=status, claim_index=claim_index,
        )

        return claim

    return _wrapper


@pytest.fixture(name='create_segment')
def _create_segment(
        create_claim_for_segment,
        create_segment_for_claim,
        taxi_cargo_claims,
        build_segment_update_request,
        get_segment_id,
):
    async def _wrapper(*, autoreorder_flow: str = None, **kwargs):
        claim_info = await create_claim_for_segment(**kwargs)
        segment_id = (
            await create_segment_for_claim(claim_info.claim_id)
        ).json()['created_segments'][0]['segment_id']

        if autoreorder_flow is not None:
            segment_id = await get_segment_id()
            response = await taxi_cargo_claims.post(
                'v1/segments/dispatch/bulk-update-state',
                json={
                    'segments': [
                        build_segment_update_request(
                            segment_id,
                            'taxi_order_id',
                            autoreorder_flow=autoreorder_flow,
                        ),
                    ],
                },
            )
            assert response.status_code == 200, 'bulk-update-state error'

        return claim_info

    return _wrapper


@pytest.fixture(name='create_segment_with_payment')
def _create_segment_with_payment(
        enable_payment_on_delivery, mock_payments_check_token, create_segment,
):
    async def _wrapper(**kwargs):
        return await create_segment(**kwargs)

    return _wrapper


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='just_client_payment_claim',
    consumers=['cargo-claims/accept'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.fixture(name='create_claim_segment_matched_car_taxi_class')
def _create_claim_segment_matched_car_taxi_class(
        taxi_cargo_claims,
        state_controller,
        create_segment_for_claim,
        get_default_corp_client_id,
        get_default_request,
        get_default_headers,
        get_segment_id,
):
    async def _wrapper(
            corp_client_id: str, taxi_class: str, *, claim_kind: str = None,
    ):
        request = copy.deepcopy(get_default_request())
        if claim_kind is not None:
            request['claim_kind'] = claim_kind
        state_controller.handlers().create.request = request

        claim_info = await state_controller.apply(target_status='estimating')

        response = await taxi_cargo_claims.post(
            f'v1/claims/finish-estimate?claim_id={claim_info.claim_id}',
            json={
                'cars': [
                    {
                        'taxi_class': taxi_class,
                        'items': [{'id': 2, 'quantity': 1}],
                    },
                ],
                'zone_id': 'moscow',
                'currency': 'RUB',
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price_raw': 999,
                    'price': '999.0010',
                },
                'is_delayed': False,
                'taxi_classes_substitution': [taxi_class],
            },
        )
        assert response.status_code == 200

        claim_info = await state_controller.apply(
            target_status='accepted', fresh_claim=False,
        )

        result = (await create_segment_for_claim(claim_info.claim_id)).json()
        assert len(result['created_segments']) == 1
        segment_id = result['created_segments'][0]['segment_id']
        return claim_info, segment_id

    return _wrapper


@pytest.fixture(name='build_segment_update_request')
def _build_segment_update_request():
    def _wrapper(
            segment_id: str,
            taxi_order_id: str,
            *,
            with_park: bool = True,
            cargo_order_id: str = CARGO_ORDER_ID,
            revision: int = 1,
            with_performer: bool = True,
            with_order: bool = True,
            resolution: str = None,
            cancel_state: str = None,
            taxi_class: str = None,
            transport_type: str = None,
            autoreorder_flow: str = None,
            driver_id: str = 'driver_id1',
            park_id: str = 'park_id1',
            lookup_version: int = 1,
            segment_revision: int = None,
            autocancel_reason: str = None,
            admin_cancel_reason: str = None,
            route_id: str = None,
            router_id: str = None,
            car_color: str = None,
            car_color_hex: str = None,
    ):
        segment_request = {'id': segment_id, 'revision': revision}
        if with_performer:
            performer = {
                'revision': 1,
                'order_alias_id': 'order_alias_id_1',
                'phone_pd_id': '+70000000000_pd',
                'name': 'Kostya',
                'driver_id': driver_id,
                'park_id': park_id,
                'park_clid': 'park_clid1',
                'car_id': 'car_id_1',
                'car_number': 'car_number_1',
                'car_model': 'car_model_1',
                'lookup_version': lookup_version,
            }
            if car_color:
                performer['car_color'] = car_color
            if car_color_hex:
                performer['car_color_hex'] = car_color_hex
            if with_park:
                performer['park_name'] = 'park_name_1'
                performer['park_org_name'] = 'park_org_name_1'

            if taxi_class:
                performer['taxi_class'] = taxi_class
            if transport_type:
                performer['transport_type'] = transport_type

            segment_request['performer_info'] = performer

        if with_order:
            segment_request['cargo_order_id'] = cargo_order_id
            segment_request['taxi_order_id'] = taxi_order_id

        if resolution is not None:
            segment_request['resolution'] = resolution

        if cancel_state is not None:
            segment_request['cancel_state'] = cancel_state

        if autoreorder_flow is not None:
            segment_request['autoreorder_flow'] = autoreorder_flow

        if segment_revision is not None:
            segment_request['claims_segment_revision'] = segment_revision

        if autocancel_reason is not None:
            segment_request['autocancel_reason'] = autocancel_reason

        if admin_cancel_reason is not None:
            segment_request['admin_cancel_reason'] = admin_cancel_reason

        if route_id is not None:
            segment_request['route_id'] = route_id

        if router_id is not None:
            segment_request['router_id'] = router_id

        return segment_request

    return _wrapper


class SegmentCreationResult:
    def __init__(
            self,
            id: str,  # pylint: disable=W0622
            claim_id: str,
            claim_info,
            cargo_order_id: str,
    ):
        self.id = id  # pylint: disable=C0103
        self.claim_id = claim_id
        self.claim_info = claim_info
        self.cargo_order_id = cargo_order_id


@pytest.fixture(name='create_segment_with_performer')
def _create_segment_with_performer(
        enable_payment_on_delivery,
        taxi_cargo_claims,
        create_segment,
        build_segment_update_request,
        state_controller,
        get_segment_id_by_claim,
):
    async def _wrapper(
            status='performer_found',
            taxi_class: str = None,
            transport_type: str = None,
            route_id: str = None,
            **kwargs,
    ) -> SegmentCreationResult:
        claim_info = await create_segment(**kwargs)
        segment_id = await get_segment_id_by_claim(claim_info.claim_id)
        update_request = build_segment_update_request(
            segment_id,
            'taxi_order_id',
            taxi_class=taxi_class,
            transport_type=transport_type,
            route_id=route_id,
        )
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={'segments': [update_request]},
        )
        assert response.status_code == 200, 'bulk-update-state error'

        return SegmentCreationResult(
            segment_id,
            claim_info.claim_id,
            claim_info,
            update_request['cargo_order_id'],
        )

    return _wrapper


@pytest.fixture(autouse=True, name='mock_virtual_tariffs')
def _mock_virtual_tariffs(mockserver, get_default_corp_client_id):
    @mockserver.json_handler('/virtual-tariffs/v1/match')
    def _handler(request):
        return {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        }

    return _handler


@pytest.fixture
async def get_final_pricing_id(pgsql):
    def _wrapper(*, claim_uuid):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""SELECT final_pricing_calc_id FROM cargo_claims.claims
                WHERE uuid_id= '{claim_uuid}'""",
        )
        return list(cursor)[0][0]

    return _wrapper


@pytest.fixture
async def fetch_claim_kind(pgsql):
    async def _wrapper(claim_id: str):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            'SELECT claim_kind '
            'FROM cargo_claims.claims '
            'WHERE uuid_id = %s ',
            (claim_id,),
        )
        result = cursor.fetchone()
        assert result
        return result[0]

    return _wrapper


@pytest.fixture(name='get_default_cargo_order_id')
async def _get_default_cargo_order_id():
    return CARGO_ORDER_ID


@pytest.fixture
async def fetch_segment_points(taxi_cargo_claims):
    async def _wrapper(segment_id: str):
        response = await taxi_cargo_claims.post(
            '/v1/segments/info', params={'segment_id': segment_id},
        )
        assert response.status_code == 200

        result = list()
        for point in response.json()['points']:
            result.append(
                {
                    'point_id': point['point_id'],
                    'type': point['segment_point_type'],
                    'visit_order': point['visit_order'],
                },
            )
        return result

    return _wrapper


@pytest.fixture
def get_segment_id_by_claim(taxi_cargo_claims):
    async def _wrapper(claim_uuid: str):
        response = await taxi_cargo_claims.post(
            '/v2/admin/claims/full', params={'claim_id': claim_uuid},
        )
        assert response.status_code == 200
        return response.json()['claim']['segments'][0]['id']

    return _wrapper


@pytest.fixture
def mock_order_proc_for_autoreorder(mocker_archive_get_order_proc, load_json):
    def wrapper(taxi_order_id='taxi_order_id_1'):
        order_proc = load_json('order_proc.json')
        order_proc['_id'] = taxi_order_id
        mocker_archive_get_order_proc(order_proc)

    return wrapper


@pytest.fixture(name='exp_cargo_reorder_decision_maker')
async def _exp_cargo_reorder_decision_maker(experiments3, taxi_cargo_claims):
    async def wrapper():
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_reorder_decision_maker',
            consumers=['cargo-claims/autoreorder'],
            clauses=[],
            default_value={'reason': 'foobar', 'is_autoreorder_enabled': True},
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payment_virtual_clients')
async def _exp_cargo_payment_virtual_clients(experiments3, taxi_cargo_claims):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payment_virtual_clients',
            consumers=['cargo-claims/accept', 'cargo-claims/create-claim'],
            clauses=[],
            default_value={'virtual_client_id': 'yandex_virtual_client'},
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_claims_grocery_shifts')
async def _exp_cargo_claims_grocery_shifts(experiments3, taxi_cargo_claims):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_grocery_shifts',
            consumers=['cargo-claims/create-claim'],
            clauses=[],
            default_value={'enabled': True},
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture
def mock_payments_check_token(mockserver):
    @mockserver.json_handler('/cargo-misc/payments/v1/check-token')
    def mock(request):
        context.last_request = request.json
        if context.status_code == 200:
            return {
                'is_valid': context.is_valid,
                'test': context.test,
                'fiscalization_enabled': context.fiscalization_enabled,
            }
        return mockserver.make_response(
            status=context.status_code, json=context.response_body,
        )

    class Context:
        def __init__(self):
            self.last_request = None
            self.status_code = 200
            self.response_body = {}
            self.is_valid = True
            self.test = True
            self.fiscalization_enabled = True
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_validate')
def _mock_payment_validate(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/validate')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_create')
def _mock_payment_create(mockserver, mock_payment_validate):
    @mockserver.json_handler('/cargo-payments/v1/payment/create')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {'payment_id': str(uuid.uuid4()), 'revision': 1}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_update')
def _mock_payment_update(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/update')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_status')
def _mock_payment_status(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/status')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {
                'payment_id': request.json['payment_id'],
                'revision': 1,
                'status': context.status,
                'is_paid': context.is_paid,
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.status = 'finished'
            self.is_paid = True
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_set_performer')
def _mock_payment_set_performer(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/set-performer')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='set_pay_on_delivering_settings')
async def _set_pay_on_delivering_settings(pgsql):
    async def wrapper(corp_client_id: str, enabled: bool = False):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO cargo_claims.payment_on_delivery_settings(
                corp_client_id, enabled
            )
            VALUES ('{corp_client_id}', {enabled})
        """,
        )

    return wrapper


@pytest.fixture
async def enable_payment_on_delivery(
        get_default_corp_client_id, set_pay_on_delivering_settings,
):
    await set_pay_on_delivering_settings(
        corp_client_id=get_default_corp_client_id, enabled=True,
    )


@pytest.fixture
async def disable_payment_on_delivery(
        get_default_corp_client_id, set_pay_on_delivering_settings,
):
    await set_pay_on_delivering_settings(
        corp_client_id=get_default_corp_client_id, enabled=False,
    )


@pytest.fixture(name='get_claim_v2')
async def _get_claim_v2(taxi_cargo_claims, get_default_headers):
    async def wrapper(*, claim_id):
        response = await taxi_cargo_claims.post(
            '/api/integration/v2/claims/info',
            params={'claim_id': claim_id},
            headers=get_default_headers(),
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='get_payment_info')
async def _get_payment_info(get_claim_v2):
    async def wrapper(*, claim_id, payment_id):
        claim = await get_claim_v2(claim_id)

        for point in claim['route_points']:
            if (
                    point.get('payment_on_delivery', {}).get('payment_ref_id')
                    == payment_id
            ):
                return point['payment_on_delivery']
        return None

    return wrapper


def get_claim_point_id_by_order(segment, visit_order):
    for point in segment['points']:
        if point['visit_order'] == visit_order:
            return point['claim_point_id']

    pytest.fail(f'No such visit_order {visit_order} in segment: {segment}')
    return None


def get_headers():
    return {
        'X-Remote-Ip': '12.34.56.78',
        'X-Real-Ip': '12.34.56.78',
        'Accept-Language': 'ru',
    }


@pytest.fixture(name='arrive_at_point')
async def _arrive_at_point(taxi_cargo_claims, get_segment):
    async def wrapper(
            segment_id: str, point_visit_order: int, driver_info=None,
    ):
        segment = await get_segment(segment_id)
        claim_point_id = get_claim_point_id_by_order(
            segment, point_visit_order,
        )

        response = await taxi_cargo_claims.post(
            '/v1/segments/arrive_at_point',
            params={'segment_id': segment_id},
            json={
                'point_id': claim_point_id,
                'idempotency_token': uuid.uuid4().hex,
                'last_known_status': TAXIMETER_STATUS_BY_STATUS[
                    segment['status']
                ],
                'driver': driver_info or DRIVER_INFO,
            },
            headers=get_headers(),
        )

        assert response.status_code == 200, 'Fixture "arrive_at_point" failed'

    return wrapper


@pytest.fixture(name='raw_exchange_init')
async def _raw_exchange_init(taxi_cargo_claims, get_segment):
    async def wrapper(segment_id: str, point_visit_order: int):
        segment = await get_segment(segment_id)
        claim_point_id = get_claim_point_id_by_order(
            segment, point_visit_order,
        )

        response = await taxi_cargo_claims.post(
            '/v1/segments/exchange/init',
            params={'segment_id': segment_id},
            json={
                'point_id': claim_point_id,
                'idempotency_token': uuid.uuid4().hex,
                'last_known_status': TAXIMETER_STATUS_BY_STATUS[
                    segment['status']
                ],
                'driver': DRIVER_INFO,
            },
            headers=get_headers(),
        )
        return response

    return wrapper


@pytest.fixture(name='exchange_init')
async def _exchange_init(raw_exchange_init):
    async def wrapper(segment_id: str, point_visit_order: int):
        response = await raw_exchange_init(segment_id, point_visit_order)
        assert response.status_code == 200
        return response

    return wrapper


@pytest.fixture(name='raw_exchange_return')
async def _raw_exchange_return(taxi_cargo_claims, get_segment):
    async def wrapper(segment_id: str, point_visit_order: int):
        segment = await get_segment(segment_id)
        claim_point_id = get_claim_point_id_by_order(
            segment, point_visit_order,
        )

        response = await taxi_cargo_claims.post(
            '/v1/segments/return',
            params={'segment_id': segment_id},
            json={
                'point_id': claim_point_id,
                'idempotency_token': uuid.uuid4().hex,
                'last_known_status': TAXIMETER_STATUS_BY_STATUS[
                    segment['status']
                ],
                'driver': DRIVER_INFO,
            },
            headers=get_headers(),
        )
        return response

    return wrapper


@pytest.fixture(name='exchange_return')
async def _exchange_return(raw_exchange_return):
    async def wrapper(segment_id: str, point_visit_order: int):
        response = await raw_exchange_return(segment_id, point_visit_order)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='raw_exchange_confirm')
async def _raw_exchange_confirm(taxi_cargo_claims, get_segment):
    async def wrapper(
            segment_id: str,
            point_visit_order: int = None,
            claim_point_id: int = None,
            with_driver: bool = True,
            paper_flow: bool = False,
            with_support: bool = False,
            last_known_status: str = None,
            skip_last_known_status: bool = False,
    ):
        segment = await get_segment(segment_id)

        assert (
            point_visit_order or claim_point_id
        ), 'Send at least one point param'

        point_id = claim_point_id
        if point_id is None:
            point_id = get_claim_point_id_by_order(segment, point_visit_order)

        if not skip_last_known_status:
            last_known_status = (
                last_known_status
                or TAXIMETER_STATUS_BY_STATUS[segment['status']]
            )

        request_body = {
            'point_id': point_id,
            'confirmation_code': '123456',
            'last_known_status': last_known_status,
            'paper_flow': paper_flow,
        }
        if with_driver:
            request_body['driver'] = {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            }
        if with_support:
            request_body['support'] = {
                'ticket': 'TICKET-100',
                'comment': 'some text',
            }

        response = await taxi_cargo_claims.post(
            '/v1/segments/exchange/confirm',
            params={'segment_id': segment_id},
            json=request_body,
            headers=get_headers(),
        )
        return response

    return wrapper


@pytest.fixture(name='exchange_confirm')
async def _exchange_confirm(raw_exchange_confirm):
    async def wrapper(*args, response_code: int = 200, **kwargs):
        response = await raw_exchange_confirm(*args, **kwargs)
        assert response.status_code == response_code
        return response

    return wrapper


@pytest.fixture(name='do_prepare_segment_state')
async def _do_prepare_segment_state(
        taxi_cargo_claims, exchange_init, exchange_confirm, arrive_at_point,
):
    async def wrapper(
            segment,
            visit_order: int,
            last_arrive_at_point: bool = True,
            last_exchange_init: bool = True,
            skip_arrive: bool = False,
            **kwargs,
    ):
        current_point_index = 1
        while current_point_index < visit_order:
            if not skip_arrive:
                await arrive_at_point(segment.id, current_point_index)
            await exchange_init(segment.id, current_point_index)
            await exchange_confirm(segment.id, current_point_index)
            current_point_index += 1

        if not skip_arrive and last_arrive_at_point:
            await arrive_at_point(segment.id, current_point_index)

        if last_exchange_init:
            await exchange_init(segment.id, visit_order)

        return segment

    return wrapper


@pytest.fixture(name='prepare_segment_state')
async def _prepare_segment_state(
        create_segment_with_performer, do_prepare_segment_state,
):
    async def wrapper(**kwargs):
        segment = await create_segment_with_performer(**kwargs)
        return await do_prepare_segment_state(segment, **kwargs)

    return wrapper


@pytest.fixture(name='prepare_state')
async def _prepare_state(prepare_segment_state):
    async def wrapper(*args, **kwargs):
        segment = await prepare_segment_state(*args, **kwargs)
        return segment.id

    return wrapper


def check_point_visited(segment, claim_point_id):
    for point in segment['points']:
        if point['claim_point_id'] == claim_point_id:
            assert point['visit_status'] == 'visited'
            assert point['resolution']['is_visited']

            return

    pytest.fail(
        f'No such claim_point_id {claim_point_id} in segment: {segment}',
    )


def check_claim_point_visited(claim, claim_point_id):
    for point in claim['route_points']:
        if point['id'] == claim_point_id:
            assert point['visit_status'] == 'visited'

            return

    pytest.fail(f'No such claim_point_id {claim_point_id} in claim: {claim}')


@pytest.fixture(name='claim_point_id_by_visit_order')
async def _claim_point_id_by_visit_order(get_segment):
    async def _wrapper(segment_id: str, visit_order: int):
        segment = await get_segment(segment_id)

        return get_claim_point_id_by_order(segment, visit_order)

    return _wrapper


@pytest.fixture(name='mock_create_event')
def _mock_create_event(mockserver):
    def mock(
            *,
            event_id='event_id_1',
            item_id=None,
            event=None,
            idempotency_token=None,
            queue='claim',
            error_code=None,
    ):
        @mockserver.json_handler(f'/processing/v1/cargo/{queue}/create-event')
        def create_event(request):
            if error_code:
                return mockserver.make_response(
                    status=error_code,
                    json={'code': 'invalid_payload', 'message': 'error'},
                )
            if item_id is not None:
                assert request.query['item_id'] == item_id
            if idempotency_token is not None:
                assert (
                    request.headers['X-Idempotency-Token'] == idempotency_token
                )
            if event is not None:
                assert request.json == event

            return {'event_id': event_id}

        return create_event

    return mock


@pytest.fixture(name='mock_robot_points_search')
def _mock_robot_points_search(mockserver):
    @mockserver.json_handler('/robot-sdc/api/points/search')
    def mock(request):
        context.last_query = request.query

        if context.response_body_iter is not None:
            response_body = next(context.response_body_iter)
        else:
            response_body = context.response_body

        return mockserver.make_response(
            status=context.status_code, json=response_body,
        )

    class Context:
        def __init__(self):
            self.last_query = None
            self.status_code = 200
            self.response_body = {'location': 100}
            self.handler = mock
            self.response_body_iter = None

    context = Context()

    return context


@pytest.fixture(name='update_point')
def _update_point(pgsql):
    def _inner(point_id=None, **kwargs):
        if not kwargs:
            return

        for field, value in kwargs.items():
            if value is None:
                kwargs[field] = 'NULL'
            elif isinstance(value, str):
                kwargs[field] = f'\'{value}\''
            elif isinstance(value, (int, float)):
                kwargs[field] = value
            else:
                assert False, 'Unknown type for conversion'

        sql = f"""
        UPDATE cargo_claims.points
        SET
        {','.join(f'{field} = {value}' for (field, value) in kwargs.items())}
        """

        if point_id is not None:
            sql += f' WHERE id = {point_id}'

        pgsql['cargo_claims'].conn.cursor().execute(sql)

    return _inner


@pytest.fixture(name='mock_cargo_pricing_calc')
def _mock_cargo_pricing_calc(mockserver):
    class CalcCtx:
        mock = None
        request = None
        pricing_case = 'paid_cancel'
        total_price = '200.999'
        calc_id = 'cargo-pricing/v1/' + 'A' * 32

    ctx = CalcCtx()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _mock(request):
        ctx.request = request.json
        return {
            'calc_id': ctx.calc_id,
            'price': ctx.total_price,
            'taxi_pricing_response': {'foo': 'bar'},
            'services': [],
            'details': {
                'pricing_case': ctx.pricing_case,
                'paid_waiting_in_destination_price': '25.0000',
                'paid_waiting_in_destination_time': '30.0000',
                'total_time': '12',
                'total_distance': '1000',
                'paid_waiting_time': '5',
                'paid_waiting_price': '50',
                'paid_waiting_in_transit_time': '5',
                'paid_waiting_in_transit_price': '50',
            },
            'units': {
                'currency': 'RUB',
                'distance': 'kilometer',
                'time': 'minute',
            },
        }

    ctx.mock = _mock
    return ctx


@pytest.fixture(name='mock_cargo_pricing_retrieve')
def _mock_cargo_pricing_retrieve(mockserver):
    class CalcCtx:
        mock = None
        request = None
        pricing_case = 'paid_cancel'
        total_price = '200.999'
        expected_calc_id = None

    ctx = CalcCtx()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
    def _mock_retrieve(request):
        if ctx.expected_calc_id:
            assert ctx.expected_calc_id == request.json['calc_id']
        ctx.request = request.json
        return {
            'calc_id': request.json['calc_id'],
            'price': ctx.total_price,
            'units': {
                'currency': 'RUB',
                'distance': 'kilometer',
                'time': 'minute',
            },
            'pricing_case': ctx.pricing_case,
            'details': {
                'paid_waiting_in_destination_price': '25.0000',
                'paid_waiting_in_destination_time': '30.0000',
                'paid_waiting_in_transit_price': '20.0000',
                'paid_waiting_in_transit_time': '0.0000',
                'paid_waiting_price': '0.0000',
                'paid_waiting_time': '60.0000',
                'pricing_case': 'default',
                'total_distance': '3541.0878',
                'total_time': '1077.0000',
            },
            'taxi_pricing_response': {},
            'request': {},
        }

    ctx.mock = _mock_retrieve
    return ctx


@pytest.fixture(name='mock_waybill_info')
def _mock_waybill_info(mockserver, load_json):
    class Context:
        response = load_json('waybill_info_response.json')
        mock = None

    context = Context()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock(request):
        return mockserver.make_response(json=context.response)

    context.mock = _mock
    return context


def get_v2_estimation_result():
    return {
        'price': {
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price': {'total': '999.0010'},
            },
            'currency_code': 'RUB',
        },
        'trip': {'zone_id': 'moscow', 'eta': 30},
        'vehicle': {
            'taxi_class': 'express',
            'taxi_requirements': {'door_to_door': True},
        },
    }


@pytest.fixture(name='get_v2_estimation_result')
def _get_v2_estimation_result():
    return get_v2_estimation_result()


@pytest.fixture(name='encode_cursor')
def _encode_cursor():
    def _encode(cursor: tp.Dict):
        return base64.b64encode(json.dumps(cursor).encode('utf-8')).decode()

    return _encode


@pytest.fixture(name='decode_cursor')
def _decode_cursor():
    def _decode(cursor: str):
        return json.loads(base64.b64decode(cursor))

    return _decode


@pytest.fixture(name='procaas_claim_status_filter')
async def _procaas_claim_status_filter(taxi_cargo_claims, experiments3):
    async def _wrapper(enabled=True, clauses=None):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_procaas_claim_status_filter',
            consumers=['cargo-claims/procaas'],
            clauses=clauses if not None else [],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture(name='procaas_event_kind_filter')
async def _procaas_event_kind_filter(taxi_cargo_claims, experiments3):
    async def _wrapper(enabled=True, clauses=None):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_procaas_event_kind_filter',
            consumers=['cargo-claims/procaas'],
            clauses=clauses if not None else [],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture(name='procaas_send_settings')
async def _procaas_send_settings(taxi_cargo_claims, experiments3):
    async def _wrapper(is_async=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_procaas_send_settings',
            consumers=['cargo-claims/procaas'],
            clauses=[],
            default_value={'accept_settings': {'is_async': is_async}},
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


@pytest.fixture(name='set_up_processing_exp')
def _set_up_processing_exp(set_up_create_experiment):
    async def _wrapper(*, processing_flow: str = None, **kwargs):
        matched = {'processing_flow': processing_flow}
        not_matched = {'processing_flow': 'disabled'}
        return await set_up_create_experiment(
            experiment='cargo_claims_processing_flow',
            matched=matched,
            not_matched=not_matched,
            **kwargs,
        )

    return _wrapper


@pytest.fixture(name='exp_cargo_waiting_times_by_point')
async def _exp_cargo_waiting_times_by_point(experiments3, taxi_cargo_claims):
    async def wrapper(enabled=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_waiting_times_by_point',
            consumers=['cargo-claims/cargo-route-watch'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'source': 3,
                'destination': 3,
                'return': 3,
            },
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


@pytest.fixture(name='get_segment_points_by_segment_id')
async def _get_segment_points_by_segment_id(get_segment):
    async def _wrapper(segment_id: str):
        segment = await get_segment(segment_id)

        return segment['points']

    return _wrapper


@pytest.fixture(name='create_segment_for_claim')
def _create_segment_for_claim(taxi_cargo_claims, mockserver):
    async def wrapper(claim_id, expect_ok=True):
        @mockserver.json_handler('/processing/v1/cargo/segment/create-event')
        def mock_create_event(request):
            assert request.json['data']['claim_uuid'] == claim_id
            assert request.query['item_id']
            return {'event_id': 'event_id_1'}

        response = await taxi_cargo_claims.post(
            '/v2/processing/segments/create', params={'claim_id': claim_id},
        )
        if expect_ok:
            assert response.status_code == 200, response.json()
            created_segments = response.json()['created_segments']
            assert len(created_segments) == 1  # one segment per claim
            assert len(created_segments) == mock_create_event.times_called
        return response

    return wrapper


@pytest.fixture(name='mock_sdd_delivery_intervals')
def _mock_sdd_delivery_intervals(mockserver):
    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def mock(request):
        return mockserver.make_response(
            status=context.status_code, json=context.response,
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.handler = mock
            self.response = {
                'available_intervals': [
                    {
                        'from': '2022-02-19T19:10:00+00:00',
                        'to': '2022-02-19T22:00:00+00:00',
                    },
                    {
                        'from': '2022-02-20T02:10:00+00:00',
                        'to': '2022-02-20T06:00:00+00:00',
                    },
                ],
            }

    context = Context()

    return context


@pytest.fixture(name='mock_cargo_pricing_confirm_usage')
def _mock_cargo_pricing_confirm_usage(mockserver):
    class Context:
        mock = None
        request = None
        response = {}

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/confirm-usage')
    def _mock(request):
        ctx.request = request.json
        return ctx.response

    ctx.mock = _mock
    return ctx


@pytest.fixture(name='mock_cargo_pricing_resolve_segment')
def _mock_cargo_pricing_resolve_segment(mockserver, load_json):
    class Context:
        request = None
        mock = None
        pricing_case = 'paid_cancel'
        response = {
            'calc_for_client': load_json('resolve_segment_response.json'),
        }

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/resolve-segment')
    def mock(request):
        ctx.request = request.json
        response = copy.copy(ctx.response)
        response['calc_for_client']['details']['algorithm'][
            'pricing_case'
        ] = ctx.pricing_case
        return response

    ctx.mock = mock
    return ctx


@pytest.fixture(name='enable_use_pricing_dragon_handlers_feature')
async def _enable_use_pricing_dragon_handlers_feature(
        taxi_cargo_claims, experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_claims_use_pricing_dragon_handlers',
        consumers=['cargo-claims/create-claim'],
        clauses=[],
        default_value={'enabled': True},
    )
    await taxi_cargo_claims.invalidate_caches()


@pytest.fixture(name='assert_segments_cancelled')
def _assert_segments_cancelled(taxi_cargo_claims, get_db_segment_ids):
    async def wrapper(is_no_pricing=False):
        segment_ids = await get_db_segment_ids()
        response = await taxi_cargo_claims.post(
            '/v1/segments/bulk-info',
            json={
                'segment_ids': [
                    {'segment_id': segment_id} for segment_id in segment_ids
                ],
            },
        )
        assert response.status_code == 200

        for segment in response.json()['segments']:
            assert segment['status'] == 'cancelled'
            assert segment['resolution'] == 'cancelled_by_user'
            assert segment['points_user_version'] > 1
            assert 'final_pricing_calc_id' in segment['pricing']
            if is_no_pricing:
                assert (
                    segment['pricing']['final_pricing_calc_id']
                    == NO_PRICING_CALC_ID
                )

            for point in segment['points']:
                assert point['visit_status'] == 'skipped'
                assert point['resolution']['is_skipped']
                assert point['is_resolved']
                assert point['revision'] > 1

    return wrapper


@pytest.fixture
def default_brand_id():
    return DEFAULT_BRAND_ID
