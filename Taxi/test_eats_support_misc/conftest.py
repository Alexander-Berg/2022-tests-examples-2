# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
import typing

import pytest

import eats_support_misc.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_support_misc.generated.service.pytest_plugins']


@pytest.fixture
def mock_fail_to_get_personal_data_value_by_id(mockserver):
    def wrapper(data_type, status, error_code, error_message):
        @mockserver.json_handler(f'personal/v1/{data_type}/retrieve')
        def _mock_request_to_personal(request):
            return mockserver.make_response(
                status=status,
                json={'code': error_code, 'message': error_message},
            )

    return wrapper


@pytest.fixture
def mock_get_personal_data_value_by_id(mockserver):
    def wrapper(personal_data_id, data_type, personal_data_value):
        @mockserver.json_handler(f'personal/v1/{data_type}/retrieve')
        def _mock_request_to_personal(request):
            assert request.json['id'] == personal_data_id
            return mockserver.make_response(
                status=200,
                json={'id': personal_data_id, 'value': personal_data_value},
            )

    return wrapper


@pytest.fixture
def mock_get_personal_id_by_value(mockserver):
    def wrapper(
            data_type: str,
            relation_dict: typing.Dict[
                str, typing.Union[str, typing.Dict[str, typing.Any]],
            ],
    ):
        @mockserver.json_handler(f'personal/v1/{data_type}/find')
        def _mock_request_to_personal(request):
            personal_data_value = request.json['value']
            result = relation_dict.get(personal_data_value)
            assert result is not None

            if isinstance(result, str):
                return mockserver.make_response(
                    status=200,
                    json={'id': result, 'value': personal_data_value},
                )

            return mockserver.make_response(
                status=result['status'],
                json={
                    'code': result['error_code'],
                    'message': result['error_message'],
                },
            )

    return wrapper


@pytest.fixture
def mock_fail_to_get_ivr_info(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/eats-core-integration-ivr/ivr-info')
        def _mock_request_to_core(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_ivr_info(mockserver):
    def wrapper(channel, phone_number, ivr_info):
        @mockserver.json_handler('/eats-core-integration-ivr/ivr-info')
        def _mock_request_to_core(request):
            assert request.query['channel'] == channel
            assert request.query['phone_number'] == phone_number
            return mockserver.make_response(status=200, json=ivr_info)

    return wrapper


@pytest.fixture
def mock_get_order_meta(mockserver):
    def wrapper(order_nr, order_meta):
        @mockserver.json_handler('/eats-core-complaint/order-meta')
        def _mock_request_to_core(request):
            assert request.query['order_nr'] == order_nr
            return mockserver.make_response(
                status=200,
                json={'request_id': order_nr, 'metadata': order_meta},
            )

    return wrapper


@pytest.fixture
def mock_fail_to_get_order_meta(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/eats-core-complaint/order-meta')
        def _mock_request_to_core(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_fail_to_get_places_info(mockserver):
    def wrapper(status):
        @mockserver.json_handler(
            '/eats-catalog-storage/internal'
            '/eats-catalog-storage/v1/places/retrieve-by-ids',
        )
        def _mock_request_to_eats_catalog_storage(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_places_info(mockserver):
    def wrapper(place_ids, projection, places_info):
        @mockserver.json_handler(
            '/eats-catalog-storage/internal'
            '/eats-catalog-storage/v1/places/retrieve-by-ids',
        )
        def _mock_request_to_eats_catalog_storage(request):
            assert request.json['place_ids'] == place_ids
            assert request.json['projection'] == projection
            return mockserver.make_response(status=200, json=places_info)

    return wrapper


@pytest.fixture
def mock_fail_to_get_claim_info(mockserver):
    def wrapper(status):
        @mockserver.json_handler(
            '/cargo-claims/api/integration/v2/claims/info',
        )
        def _mock_request_to_cargo_claims(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_claim_info(mockserver):
    def wrapper(claim_id, corp_client_id, claim_info):
        @mockserver.json_handler(
            '/cargo-claims/api/integration/v2/claims/info',
        )
        def _mock_request_to_cargo_claims(request):
            assert request.query['claim_id'] == claim_id
            assert request.headers['X-B2B-Client-Id'] == corp_client_id
            return mockserver.make_response(status=200, json=claim_info)

    return wrapper


@pytest.fixture
def mock_fail_to_get_claim_id_and_alias(mockserver):
    def wrapper(status):
        @mockserver.json_handler(
            '/eats-orders-tracking/internal/eats-orders-tracking'
            '/v1/get-claim-by-order-nr',
        )
        def _mock_request_to_cargo_claims(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_claim_id_and_alias(mockserver):
    def wrapper(order_nr, claim_id, claim_alias):
        @mockserver.json_handler(
            '/eats-orders-tracking/internal/eats-orders-tracking'
            '/v1/get-claim-by-order-nr',
        )
        def _mock_request_to_cargo_claims(request):
            assert request.query['order_nr'] == order_nr
            return mockserver.make_response(
                status=200,
                json={
                    'order_nr': order_nr,
                    'claim_id': claim_id,
                    'claim_alias': claim_alias,
                },
            )

    return wrapper


@pytest.fixture
def mock_fail_to_get_points_eta(mockserver):
    def wrapper(status):
        @mockserver.json_handler(
            '/cargo-claims/api/integration/v1/claims/points-eta',
        )
        def _mock_request_to_cargo_claims(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_points_eta(mockserver):
    def wrapper(claim_id, corp_client_id, points_info):
        @mockserver.json_handler(
            '/cargo-claims/api/integration/v1/claims/points-eta',
        )
        def _mock_request_to_cargo_claims(request):
            assert request.query['claim_id'] == claim_id
            assert request.headers['X-B2B-Client-Id'] == corp_client_id
            return mockserver.make_response(
                status=200, json={'id': claim_id, 'route_points': points_info},
            )

    return wrapper


@pytest.fixture
def mock_fail_to_get_eta_to_place(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/eats-eta/v1/eta/order/courier-arrival-at')
        def _mock_request_to_eats_eta(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_eta_to_place(mockserver):
    def wrapper(order_nr, place_eta_info):
        @mockserver.json_handler('/eats-eta/v1/eta/order/courier-arrival-at')
        def _mock_request_to_eats_eta(request):
            assert request.json['order_nr'] == order_nr
            assert request.json['check_status'] is True
            return mockserver.make_response(status=200, json=place_eta_info)

    return wrapper


@pytest.fixture
def mock_fail_to_get_eta_to_eater(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/eats-eta/v1/eta/order/delivery-at')
        def _mock_request_to_eats_eta(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_eta_to_eater(mockserver):
    def wrapper(order_nr, eater_eta_info):
        @mockserver.json_handler('/eats-eta/v1/eta/order/delivery-at')
        def _mock_request_to_eats_eta(request):
            assert request.json['order_nr'] == order_nr
            assert request.json['check_status'] is True
            return mockserver.make_response(status=200, json=eater_eta_info)

    return wrapper


@pytest.fixture
def mock_fail_to_get_receipts(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/eats-receipts/api/v1/receipts')
        def _mock_request_to_eats_receipts(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_receipts(mockserver):
    def wrapper(order_nr, receipts_info):
        @mockserver.json_handler('/eats-receipts/api/v1/receipts')
        def _mock_request_to_eats_receipts(request):
            assert request.json['order_id'] == order_nr
            return mockserver.make_response(status=200, json=receipts_info)

    return wrapper


@pytest.fixture
def mock_fail_to_check_text(mockserver):
    def wrapper(status):
        @mockserver.json_handler('/clean-web-eats/v2')
        def _mock_request_to_eats_receipts(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_check_text(mockserver):
    def wrapper(text, result):
        @mockserver.json_handler('/clean-web-eats/v2')
        def _mock_request_to_eats_receipts(request):
            assert request.json['method'] == 'process'
            assert request.json['params']['type'] == 'text'
            assert request.json['params']['service'] == 'eda'
            assert request.json['params']['body'] == {'text': text}
            return mockserver.make_response(status=200, json=result)

    return wrapper


@pytest.fixture
def mock_brands_find_by_id(mockserver):
    def wrapper(brand_id: int, brand_info: typing.Dict[str, typing.Any]):
        @mockserver.json_handler('/eats-brands/brands/v1/find-by-id')
        def _mock_request_to_eats_brand(request):
            assert request.json['id'] == brand_id
            return mockserver.make_response(status=200, json=brand_info)

    return wrapper


@pytest.fixture
def mock_fail_brands_find_by_id(mockserver):
    def wrapper(status: int, code: str, message: str):
        @mockserver.json_handler('/eats-brands/brands/v1/find-by-id')
        def _mock_request_to_eats_brand(request):
            return mockserver.make_response(
                status=status, json={'code': code, 'message': message},
            )

    return wrapper


@pytest.fixture
def mock_couriers_core_find_by_id(mockserver):
    def wrapper(courier_id: str, courier_info: typing.Dict[str, typing.Any]):
        @mockserver.json_handler(
            f'couriers-core/api/v1/general-information/couriers/{courier_id}',
        )
        def _mock_request_to_couriers_core(request):
            return mockserver.make_response(status=200, json=courier_info)

    return wrapper


@pytest.fixture
def mock_fail_couriers_core_find_by_id(mockserver):
    def wrapper(
            courier_id: str,
            status: str,
            error_domain: str,
            error_code: str,
            error_message: str,
            errors: typing.Dict[str, typing.List[str]],
    ):
        @mockserver.json_handler(
            f'couriers-core/api/v1/general-information/couriers/{courier_id}',
        )
        def _mock_request_to_couriers_core(request):
            return mockserver.make_response(
                status=status,
                json={
                    'domain': error_domain,
                    'code': error_code,
                    'err': error_message,
                    'errors': errors,
                },
            )

    return wrapper


@pytest.fixture
def mock_couriers_core_find_by_phone(mockserver):
    def wrapper(
            courier_phone: str, courier_info: typing.Dict[str, typing.Any],
    ):
        @mockserver.json_handler(
            'couriers-core/api/v1/general-information/'
            'couriers/catalog/search',
        )
        def _mock_request_to_couriers_core(request):
            assert f'+{request.query["phone"]}' == courier_phone
            return mockserver.make_response(status=200, json=courier_info)

    return wrapper


@pytest.fixture
def mock_fail_couriers_core_find_by_phone(mockserver):
    def wrapper(
            status: str,
            error_domain: str,
            error_code: str,
            error_message: str,
            errors: typing.Dict[str, typing.List[str]],
    ):
        @mockserver.json_handler(
            'couriers-core/api/v1/general-information/'
            'couriers/catalog/search',
        )
        def _mock_request_to_couriers_core(request):
            return mockserver.make_response(
                status=status,
                json={
                    'domain': error_domain,
                    'code': error_code,
                    'err': error_message,
                    'errors': errors,
                },
            )

    return wrapper


@pytest.fixture
def mock_eats_eaters_find_eaters_by_phone_id(mockserver):
    def wrapper(
            personal_phone_id: str,
            list_of_eaters_info: typing.List[
                typing.Dict[str, typing.Any]
            ] = None,
            status: int = 200,
    ):
        @mockserver.json_handler(
            'eats-eaters/v1/eaters/find-by-personal-phone-id',
        )
        def _mock_request_to_eats_eaters(request):
            assert request.json['personal_phone_id'] == personal_phone_id
            return mockserver.make_response(
                status=status, json=list_of_eaters_info,
            )

    return wrapper


@pytest.fixture
def mock_get_robocall_info(mockserver):
    def wrapper(claim_id: str, robocall_info: typing.Dict[str, typing.Any]):
        @mockserver.json_handler(
            'cargo-orders/internal/cargo-orders/v1/robocall/info',
        )
        def _mock_request_to_cargo_orders(request):
            assert request.query['claim_id'] == claim_id
            return mockserver.make_response(status=200, json=robocall_info)

    return wrapper


@pytest.fixture
def mock_fail_to_get_robocall_info(mockserver):
    def wrapper(status: int):
        @mockserver.json_handler(
            'cargo-orders/internal/cargo-orders/v1/robocall/info',
        )
        def _mock_request_to_cargo_orders(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_get_eater_tags(mockserver):
    def wrapper(eater_phone_id: str, eater_tags: typing.List[str]):
        @mockserver.json_handler('eats-tags/v2/match_single')
        def _mock_request_to_eats_tags(request):
            assert request.json['match'] == [
                {'type': 'personal_phone_id', 'value': eater_phone_id},
            ]
            return mockserver.make_response(
                status=200, json={'tags': eater_tags},
            )

    return wrapper


@pytest.fixture
def mock_fail_to_get_eater_tags(mockserver):
    def wrapper(status: int):
        @mockserver.json_handler('eats-tags/v2/match_single')
        def _mock_request_to_eats_tags(request):
            return mockserver.make_response(status=status, json={})

    return wrapper


@pytest.fixture
def mock_init_chatterbox_task(mockserver):
    def wrapper(
            response_status: int,
            response_data: typing.Dict,
            chat_type: str,
            message: str,
            eats_user_id: str,
            user_phone_pd_id: str,
            order_nr: str,
            yandex_uid: typing.Optional[str] = None,
            status: typing.Optional[str] = None,
            metadata: typing.Optional[typing.Dict] = None,
    ):
        @mockserver.json_handler(
            f'chatterbox/v2/tasks/init_with_tvm/{chat_type}',
        )
        def _mock_request_to_chatterbox(request):
            assert request.json['message'] == message
            assert request.json['eats_user_id'] == eats_user_id
            assert request.json['user_phone_pd_id'] == user_phone_pd_id
            assert request.json.get('user_uid') == yandex_uid
            assert request.json['eats_order_id'] == order_nr
            assert request.json.get('status') == status
            assert request.json.get('metadata') == metadata

            assert response_status in (200, 409)

            return mockserver.make_response(
                status=response_status, json=response_data,
            )

    return wrapper


@pytest.fixture
def mock_fail_to_init_task(mockserver):
    def wrapper(status: int, chat_type: str):
        @mockserver.json_handler(
            f'chatterbox/v2/tasks/init_with_tvm/{chat_type}',
        )
        def _mock_request_to_chatterbox(request):
            return mockserver.make_response(status=status)

    return wrapper


@pytest.fixture
def mock_reopen_chatterbox_task(mockserver):
    def wrapper(
            task_id: str,
            protected_statuses: typing.Optional[typing.List[str]] = None,
    ):
        @mockserver.json_handler(
            f'chatterbox/v1/tasks/{task_id}/reopen_with_tvm',
        )
        def _mock_request_to_chatterbox(request):
            assert request.json.get('protected_statuses') == protected_statuses

            return mockserver.make_response(status=200)

    return wrapper


@pytest.fixture
def mock_fail_to_reopen_task(mockserver):
    def wrapper(status: int, task_id: str):
        @mockserver.json_handler(
            f'chatterbox/v1/tasks/{task_id}/reopen_with_tvm',
        )
        def _mock_request_to_chatterbox(request):
            return mockserver.make_response(status=status)

    return wrapper


@pytest.fixture
def mock_add_hidden_comment_to_task(mockserver):
    def wrapper(
            task_id: str,
            hidden_comment: str,
            hidden_comment_metadata: typing.Optional[typing.Dict] = None,
    ):
        @mockserver.json_handler(
            f'chatterbox/v1/tasks/{task_id}/hidden_comment_with_tvm',
        )
        def _mock_request_to_chatterbox(request):
            assert request.json['hidden_comment'] == hidden_comment
            assert (
                request.json.get('hidden_comment_metadata')
                == hidden_comment_metadata
            )

            return mockserver.make_response(status=200)

    return wrapper


@pytest.fixture
def mock_fail_to_add_hidden_comment(mockserver):
    def wrapper(status: int, task_id: str):
        @mockserver.json_handler(
            f'chatterbox/v1/tasks/{task_id}/hidden_comment_with_tvm',
        )
        def _mock_request_to_chatterbox(request):
            return mockserver.make_response(status=status)

    return wrapper
