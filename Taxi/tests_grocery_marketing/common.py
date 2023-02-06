import copy
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Set

# Generated via `tvmknife unittest service -s 123 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIexCpEg:PkDHYmG'
    'PZmF01QRRlgate8JvdS2HrShQxHIsr9x3tuUSrcex'
    '_RkAId_QbiPURL8oSGUscDwFiDgBde0ZAFsj_Qq1h'
    'NnCSnAV_ygcAY2a_hoIIQzDhcUKtHgmS7x5YjTaog'
    'BHVF3ZC6lrWfqwmAxdGsavk_3ncMXJxDM25ygJK6Y'
)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_ADMIN_RULES_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-YaTaxi-Draft-Author': 'user',
    'X-YaTaxi-Draft-Tickets': 'ticket-1',
    'X-YaTaxi-Draft-Id': 'grocery_draft_id',
}

YANDEX_UID = 'user-uid'
TAXI_USER_ID = 'uu298rjd91'
SESSION = f'taxi:{TAXI_USER_ID}'
APPMETRICA_DEVICE_ID = 'some-appmetrica'
EATS_USER_ID = 'eats-user-id-1'
PAYMENT_ID = 'some-payment'
PERSONAL_PHONE_ID = 'some-personal-phone-id'

DEFAULT_USER_HEADERS = {
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': (
        f'eats_user_id={EATS_USER_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
    ),
    'X-Idempotency-Token': 'idempotency-token',
    'X-YaTaxi-Session': SESSION,
    'X-Yandex-UID': YANDEX_UID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
    'X-YaTaxi-UserId': TAXI_USER_ID,
}

DEFAULT_USER_HEADERS_WITHOUT_UID = {
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': f'eats_user_id={EATS_USER_ID}, personal_phone_id=222',
    'X-Idempotency-Token': 'idempotency-token',
    'X-YaTaxi-Session': SESSION,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
    'X-YaTaxi-UserId': TAXI_USER_ID,
}

DEFAULT_UNAUTHORIZED_USER_HEADERS = {
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': 'eats_user_id=111, personal_phone_id=222',
    'X-Idempotency-Token': 'idempotency-token',
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
    'X-YaTaxi-UserId': TAXI_USER_ID,
}

DEFAULT_SCHEDULE = {
    'timezone': 'LOCAL',
    'intervals': [{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}],
}

VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:01+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}

RULE_ID_CONDITION = {'condition_name': 'rule_id', 'values': ['some_tag']}

ADD_RULES_URL = 'admin/v1/marketing/v1/match-tags/add-rules'
ADD_RULES_CHECK_URL = 'admin/v1/marketing/v1/match-tags/add-rules/check'

CHANGE_RULES_END_TIME_URL = (
    'admin/v1/marketing/v1/match-tags/change-end-rules-time'
)
CHANGE_RULES_END_TIME_CHECK_URL = (
    'admin/v1/marketing/v1/match-tags/change-end-rules-time/check'
)


def check_tags(response_json, subquery_id, hierarchy_name, tags):
    assert response_json['match_results']
    subquery_results = next(
        item
        for item in response_json['match_results']
        if item['subquery_id'] == subquery_id
    )
    assert subquery_results['results']
    result = next(
        item
        for item in subquery_results['results']
        if item['hierarchy_name'] == hierarchy_name
    )
    assert result['status'] == 'ok'
    assert result['tags'] == tags, result['tags']


def check_fetch_tags(response_json, hierarchy_name, tags):
    assert response_json['match_results']
    result = next(
        item
        for item in response_json['match_results']
        if item['hierarchy_name'] == hierarchy_name
    )
    assert result['status'] == 'ok'
    assert result['tags'] == tags


def remove_revision(input_json):
    assert input_json['match_results']
    for item in input_json['match_results']:
        for tag in item['tags']:
            tag.pop('revision', None)
    return input_json


def get_headers():
    return {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


def get_draft_headers(draft_id: Optional[str] = None):
    return {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-YaTaxi-Draft-Author': 'user',
        'X-YaTaxi-Draft-Tickets': 'ticket-1',
        'X-YaTaxi-Draft-Id': (
            draft_id if draft_id else 'grocery_marketing_draft_id'
        ),
    }


def tags_count(pgsql, hierarchy_name: str) -> int:
    pg_cursor = pgsql['grocery_marketing'].cursor()
    pg_cursor.execute(
        f"""SELECT COUNT(*)
            FROM grocery_marketing.match_rules_{hierarchy_name};""",
    )
    return list(pg_cursor)[0][0]


def get_revision(pgsql) -> int:
    pg_cursor = pgsql['grocery_marketing'].cursor()
    pg_cursor.execute(
        f"""SELECT last_value
            FROM grocery_marketing.match_rules_revision;""",
    )
    return list(pg_cursor)[0][0]


def small_menu_tag(description: str = '1') -> dict:
    return {
        'description': description,
        'values_with_schedules': [
            {
                'value': {'tag': 'some_tag_2', 'kind': 'marketing'},
                'schedule': DEFAULT_SCHEDULE,
            },
        ],
    }


async def check_add_rules_validation(
        taxi_grocery_marketing,
        pgsql,
        handler: str,
        additional_request_fields: dict,
        hierarchy_name: str,
        rules: List[dict],
        tag: dict,
        expected_status_code: int,
        expected_response: Optional[dict],
        expected_revisions_count: int = 0,
) -> Optional[List[int]]:
    start_tags_count = tags_count(pgsql, hierarchy_name)

    request: dict = {
        'rules': rules,
        'data': {'hierarchy_name': hierarchy_name, 'tag': tag},
    }
    request.update(additional_request_fields)

    if handler == ADD_RULES_CHECK_URL:
        headers = get_headers()
    else:
        headers = get_draft_headers('draft_id_check_add_rules_validation')

    response = await taxi_grocery_marketing.post(
        handler, request, headers=headers,
    )
    assert response.status_code == expected_status_code, response.json()
    end_tags_count = tags_count(pgsql, hierarchy_name)

    if expected_status_code == 200:
        if handler == ADD_RULES_URL:
            assert end_tags_count != start_tags_count
            assert response.json() == {}
            return None
        response_json = response.json()
        revisions: List[int] = response_json['data'].pop('revisions')
        assert len(revisions) == expected_revisions_count
        data: dict = {'rules': request['rules'], 'data': request['data']}
        assert response_json == {
            'data': data,
            'lock_ids': [
                {'custom': True, 'id': str(revision)} for revision in revisions
            ],
        }
        assert end_tags_count == start_tags_count
        return revisions
    response_json = response.json()
    details = response_json.get('details')
    if details is not None:
        response_json.pop('details')
    assert response_json == expected_response
    assert end_tags_count == start_tags_count
    return None


def make_response_matched_tags(tags: List[dict]) -> int:
    """
    Returns maximal encountered revision or 0
    """
    max_revision = 0
    for tag in tags:
        revision = tag.get('revision')
        if revision:
            assert isinstance(revision, int)
            if revision > max_revision:
                max_revision = revision
            tag.pop('revision')

        match_path = tag.get('match_path')
        if match_path:
            tag['match_path'].sort(
                key=lambda condition: condition['condition_name'],
            )
    tags.sort(key=lambda tag: tag['tag'].get('description'))
    return max_revision


def make_response_matched_results(match_results: List[dict]) -> None:
    match_results.sort(key=lambda result: result['hierarchy_name'])
    for result in match_results:
        make_response_matched_tags(result['tags'])


def _prepare_match_tags_response(response_json: dict) -> None:
    match_results = response_json['match_results']
    match_results.sort(key=lambda result: result['subquery_id'])
    for match_result in match_results:
        make_response_matched_results(match_result['results'])


def make_expected_matched_results(
        match_results: List[dict],
        unique_hierarchy_names: Set[str],
        show_match_parameters: bool,
) -> List[dict]:
    match_results = [
        result
        for result in match_results
        if result['hierarchy_name'] in unique_hierarchy_names
    ]
    for match_result in match_results:
        for tag in match_result['tags']:
            if not show_match_parameters:
                tag.pop('match_path')
    return match_results


def _prepare_match_tags_expected_data(
        expected_data: dict,
        unique_hierarchy_names: Set[str],
        show_match_parameters: bool,
) -> None:
    for match_result in expected_data['match_results']:
        match_result['results'] = make_expected_matched_results(
            match_result['results'],
            unique_hierarchy_names,
            show_match_parameters,
        )


def active_period_value(active_period: dict) -> dict:
    return {
        'condition_name': active_period['condition_name'],
        'value': active_period['values'][0],
    }


def rule_id_condition_value(rule_id_condition: dict) -> dict:
    return {
        'condition_name': rule_id_condition['condition_name'],
        'value': rule_id_condition['values'][0],
    }


async def check_match_tags(
        taxi_grocery_marketing,
        hierarchy_names: List[str],
        subqueries: List[dict],
        common_conditions: Optional[List[dict]],
        request_time: str,
        request_time_zone: str,
        show_match_parameters: bool,
        expected_data: dict,
        expected_status_code: int,
):
    expected_data = copy.deepcopy(expected_data)

    request = {
        'show_path': show_match_parameters,
        'request_time': request_time,
        'request_timezone': request_time_zone,
        'hierarchy_names': hierarchy_names,
        'subqueries': subqueries,
    }
    if common_conditions is not None:
        request['common_conditions'] = common_conditions

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/match-tags/', request, headers=get_headers(),
    )

    assert response.status_code == expected_status_code
    if expected_status_code != 200:
        return

    response_json = response.json()
    _prepare_match_tags_response(response_json)

    unique_hierarchy_names = set(hierarchy_names)
    _prepare_match_tags_expected_data(
        expected_data, unique_hierarchy_names, show_match_parameters,
    )
    assert response_json == expected_data


async def check_search_rules(
        taxi_grocery_marketing,
        hierarchy_name: str,
        conditions: List[dict],
        limit: int,
        offset: Optional[int],
        expected_data: Optional[dict],
        expected_status_code: int,
):
    def _make_expected_rules(
            expected_data: Optional[dict], hierarchy_name: str,
    ) -> Optional[dict]:
        if expected_data is None:
            return None
        return {
            'tag_data': {
                'hierarchy_name': hierarchy_name,
                'tags': expected_data[hierarchy_name],
            },
        }

    expected_data = copy.deepcopy(expected_data)

    request = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'limit': limit,
    }

    if offset is not None:
        request['offset'] = offset

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/match-tags/search-rules/',
        request,
        headers=get_headers(),
    )

    assert response.status_code == expected_status_code

    response_json = response.json()
    if expected_status_code != 200:
        if expected_data is not None:
            assert response_json == expected_data
        return

    make_response_matched_tags(response_json['tag_data']['tags'])
    expected_data = _make_expected_rules(expected_data, hierarchy_name)

    assert response_json == expected_data


async def add_rules(
        taxi_grocery_marketing, pgsql, add_rules_data: Dict[str, List[dict]],
) -> None:
    for hierarchy_name, data_items in add_rules_data.items():
        for data in data_items:
            await check_add_rules_validation(
                taxi_grocery_marketing,
                pgsql,
                ADD_RULES_URL,
                {'revisions': []},
                hierarchy_name,
                data['rules'],
                data['tag'],
                200,
                None,
            )


def get_added_tag(
        add_rules_data: dict, hierarchy_name: str, add_index: int = 0,
) -> dict:
    tag = copy.deepcopy(add_rules_data[hierarchy_name][add_index]['tag'])
    return tag


def get_matched_tag(
        add_rules_data: dict,
        hierarchy_name: str,
        matched_index: int = 0,
        add_index: int = 0,
) -> dict:
    tag = get_added_tag(add_rules_data, hierarchy_name, add_index)
    result: dict = {}

    max_set_apply_count = tag.get('max_set_apply_count')
    if max_set_apply_count is not None:
        result['max_set_apply_count'] = max_set_apply_count

    number_of_products = tag.get('number_of_products')
    if number_of_products is not None:
        result['number_of_products'] = number_of_products

    tag_meta = tag.get('tag_meta')
    if tag_meta is not None:
        result['tag_meta'] = tag_meta

    matched_value = tag['values_with_schedules'][matched_index]

    value = matched_value.get('value')
    if value is not None:
        result['value'] = value

    return result


def menu_match_path(
        active_period: Optional[dict] = None,
        rule_id_condition: Optional[dict] = None,
) -> dict:
    if not active_period:
        active_period = VALID_ACTIVE_PERIOD
    if not rule_id_condition:
        rule_id_condition = RULE_ID_CONDITION
    return {
        'match_path': [
            active_period_value(active_period),
            {'condition_name': 'city', 'value': '213'},
            {'condition_name': 'country', 'value': 'some_country'},
            {'condition_name': 'depot', 'value': 'some_depot'},
            {'condition_name': 'group', 'value_type': 'Other'},
            {'condition_name': 'product', 'value_type': 'Other'},
            rule_id_condition_value(rule_id_condition),
        ],
    }


def get_match_path(
        hierarchy_name: str, active_period: Optional[dict] = None,
) -> dict:
    if hierarchy_name == 'menu_tags':
        return menu_match_path(active_period)
    raise Exception(f'Unsupported hierarhy {hierarchy_name}')


def get_add_rules_data(
        active_period: Optional[dict] = None,
        rule_id_condition: Optional[dict] = None,
        hierarchy_names: FrozenSet[str] = frozenset(['menu_tags']),
        description: str = '1',
) -> dict:
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD
    if rule_id_condition is None:
        rule_id_condition = RULE_ID_CONDITION

    result = dict()
    if 'menu_tags' in hierarchy_names:
        result['menu_tags'] = [
            {
                'rules': [
                    active_period,
                    rule_id_condition,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                'tag': small_menu_tag(description),
            },
        ]

    return result


def get_full_add_rules_data(
        active_period: Optional[dict] = None,
        rule_id_condition: Optional[dict] = None,
):
    if active_period is None:
        active_period = VALID_ACTIVE_PERIOD
    if rule_id_condition is None:
        rule_id_condition = RULE_ID_CONDITION

    return {
        'menu_tags': [
            {
                'rules': [
                    active_period,
                    rule_id_condition,
                    {'condition_name': 'city', 'values': ['213']},
                    {'condition_name': 'country', 'values': ['some_country']},
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                'tag': {
                    'description': '1',
                    'tag_meta': {
                        'menu_tag': 'meta',
                        'tanker_keys': {
                            'title': 'title',
                            'subtitle': 'subtitle',
                            'payment_method_subtitle': (
                                'payment_method_subtitle'
                            ),
                        },
                        'picture': 'picture',
                        'is_expiring': False,
                        'is_price_strikethrough': True,
                    },
                    'values_with_schedules': [
                        {
                            'value': {'kind': 'promocode', 'tag': 'some_tag'},
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [{'exclude': False, 'day': [5]}],
                            },
                        },
                    ],
                },
            },
        ],
    }


def remove_hierarchy(pgsql, hierarchy_name: str) -> None:
    pg_cursor = pgsql['grocery_marketing'].cursor()
    pg_cursor.execute(
        f"""DELETE FROM grocery_marketing.match_hierarchy_conditions
           WHERE hierarchy_id IN (
               SELECT hierarchy_id
               FROM grocery_marketing.match_hierarchy
               WHERE name = '{hierarchy_name}'
           );""",
    )
    pg_cursor.execute(
        f"""DELETE FROM grocery_marketing.match_hierarchy
           WHERE name = '{hierarchy_name}';""",
    )


async def inc_stat_value(
        taxi_grocery_marketing,
        headers,
        yandex_uid,
        tag,
        order_id,
        payment_id=PAYMENT_ID,
):
    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/increment',
        json={'tag': tag, 'order_id': order_id, 'payment_id': payment_id},
        headers={**headers, 'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == 200

    return response.json()['usage_count']
