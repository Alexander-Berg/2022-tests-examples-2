# type: ignore[list-item]
import pytest

from tests_fleet_transactions_api import utils


ENDPOINT_BASE_URL = 'v1/parks/transactions/categories/list/by-'
FLEET_ENDPOINT_URL = 'fleet/transactions/v1/parks/categories/list'


def _make_groups(categories):
    groups_ids = set()
    groups = []
    for category in categories:
        if category['group_id'] in groups_ids:
            continue
        groups_ids.add(category['group_id'])
        groups.append(
            {
                'group_id': category['group_id'],
                'group_name': category.get('group_name', category['group_id']),
            },
        )
    return groups


def _apply_categories_query(query, categories):
    def _is_match_query(query, input_category):
        for field in [
                'is_enabled',
                'is_editable',
                'is_creatable',
                'is_affecting_driver_balance',
        ]:
            if (
                    query.get(field, input_category[field])
                    != input_category[field]
            ):
                return False
        return True

    return [x for x in categories if _is_match_query(query, x)]


def make_request_base(category=None, park_id='park_id_test'):
    return {
        'query': {
            'park': {'id': park_id},
            **({'category': category} if category is not None else {}),
        },
    }


def make_request_fleet(category=None, **kwargs):
    return category or {}


def make_response_base(load_json, query, creatable_ids):
    categories = load_json('main_categories.json')
    for category in categories:
        if category['id'] in creatable_ids:
            category.update({'is_creatable': True})
    return {'categories': _apply_categories_query(query, categories)}


def make_response_fleet(load_json, query, creatable_ids):
    response = make_response_base(load_json, query, creatable_ids)
    response['groups'] = _make_groups(response['categories'])
    return response


def make_headers_base(input_headers, language='ru', **kwargs):
    return {**input_headers, 'Accept-Language': language}


def make_headers_fleet(input_headers, language='ru', park_id='park_id_test'):
    headers = make_headers_base(input_headers, language)
    headers['X-Park-Id'] = park_id
    return headers


OK_PARAMS = [
    (
        'user',
        ENDPOINT_BASE_URL,
        utils.DISPATCHER_HEADERS,
        make_headers_base,
        make_request_base,
        make_response_base,
        ['partner_service_manual_dispatcher'],
    ),
    (
        'user',
        ENDPOINT_BASE_URL,
        utils.TECH_SUPPORT_HEADERS,
        make_headers_base,
        make_request_base,
        make_response_base,
        ['partner_service_manual_support'],
    ),
    (
        'fleet-api',
        ENDPOINT_BASE_URL,
        utils.FLEET_API_HEADERS,
        make_headers_base,
        make_request_base,
        make_response_base,
        ['partner_service_manual_api'],
    ),
    (
        'platform',
        ENDPOINT_BASE_URL,
        utils.PLATFORM_HEADERS,
        make_headers_base,
        make_request_base,
        make_response_base,
        [],
    ),
    (
        '',
        FLEET_ENDPOINT_URL,
        utils.DISPATCHER_HEADERS,
        make_headers_fleet,
        make_request_fleet,
        make_response_fleet,
        ['partner_service_manual_dispatcher'],
    ),
    (
        '',
        FLEET_ENDPOINT_URL,
        utils.TECH_SUPPORT_HEADERS,
        make_headers_fleet,
        make_request_fleet,
        make_response_fleet,
        ['partner_service_manual_support'],
    ),
]


@pytest.mark.parametrize(
    'postfix, endpoint, headers, make_headers,'
    'make_request, make_response, creatable_ids',
    OK_PARAMS,
)
@pytest.mark.parametrize('is_enabled', [None, False, True])
@pytest.mark.parametrize('is_editable', [None, False, True])
@pytest.mark.parametrize('is_creatable', [None, False, True])
@pytest.mark.parametrize('is_affecting_driver_balance', [None, False, True])
async def test_ok(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        mock_fleet_parks_list,
        taxi_config,
        load_json,
        postfix,
        endpoint,
        headers,
        make_headers,
        make_request,
        make_response,
        creatable_ids,
        is_enabled,
        is_editable,
        is_creatable,
        is_affecting_driver_balance,
):
    taxi_config.set_values(load_json('main_config.json'))
    category = {
        **({} if is_enabled is None else {'is_enabled': is_enabled}),
        **({} if is_editable is None else {'is_editable': is_editable}),
        **({} if is_creatable is None else {'is_creatable': is_creatable}),
        **(
            {}
            if is_affecting_driver_balance is None
            else {'is_affecting_driver_balance': is_affecting_driver_balance}
        ),
    }
    response = await taxi_fleet_transactions_api.post(
        endpoint + postfix,
        headers=make_headers(input_headers=headers),
        json=make_request(category=category),
    )

    assert response.status_code == 200, response.text
    assert response.json() == make_response(load_json, category, creatable_ids)


@pytest.mark.parametrize(
    'postfix, endpoint, headers, make_headers,'
    'make_request, _make_response, _creatable_ids',
    OK_PARAMS,
)
async def test_park_not_found(
        taxi_fleet_transactions_api,
        dispatcher_access_control,
        mock_fleet_parks_list,
        postfix,
        endpoint,
        headers,
        make_headers,
        make_request,
        _make_response,
        _creatable_ids,
):
    park_id = 'nonexistent'
    response = await taxi_fleet_transactions_api.post(
        endpoint + postfix,
        headers=make_headers(input_headers=headers, park_id=park_id),
        json=make_request(park_id=park_id),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park with id `nonexistent` not found',
    }

    assert mock_fleet_parks_list.mock_parks_list.times_called == 1


@pytest.mark.parametrize(
    'endpoint, make_headers, make_request',
    (
        (FLEET_ENDPOINT_URL, make_headers_fleet, make_request_fleet),
        (ENDPOINT_BASE_URL + 'user', make_headers_base, make_request_base),
    ),
)
async def test_forbidden(
        taxi_fleet_transactions_api,
        mock_fleet_parks_list,
        mockserver,
        endpoint,
        make_headers,
        make_request,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def dispatcher_access_control(request):
        request.get_data()
        return {'users': []}

    response = await taxi_fleet_transactions_api.post(
        endpoint,
        headers=make_headers(input_headers=utils.DISPATCHER_HEADERS),
        json=make_request(),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'dispatcher does not exist or deactivated',
    }
    assert dispatcher_access_control.times_called >= 1
