# pylint: disable=redefined-outer-name
import dataclasses
import enum
import types
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
import uuid

import pytest

SERIES_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:01+00:00',
            'is_start_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
            'is_end_utc': False,
        },
    ],
}


class ValuesType(enum.Enum):
    ANY = 'ANY'
    OTHER = 'OTHER'
    TYPE = 'TYPE'


@dataclasses.dataclass(frozen=True)
class ConditionDescription:
    condition_name: str
    type: str
    default: dict
    support_any: bool
    support_other: bool
    exclusions_for_any: bool
    exclusions_for_other: bool
    exclusions_for_type: bool

    def get_rule(
            self,
            values_type: ValuesType = ValuesType.TYPE,
            has_exclusions: bool = False,
            optional_value_pattern: Optional[str] = None,
            active_period: Optional[dict] = None,
    ) -> dict:
        value_pattern = (
            'some_{self.condition_name}'
            if optional_value_pattern is None
            else optional_value_pattern
        )
        rule: dict
        if self.condition_name == 'active_period':
            return (
                VALID_ACTIVE_PERIOD if active_period is None else active_period
            )

        if values_type is ValuesType.ANY:
            rule = {'condition_name': self.condition_name, 'values': 'Any'}
        elif values_type is ValuesType.OTHER:
            rule = {'condition_name': self.condition_name, 'values': 'Other'}
        elif self.type == 'text':
            rule = {
                'condition_name': self.condition_name,
                'values': [value_pattern.format(self=self)],
            }
        elif self.type == 'array':
            rule = {
                'condition_name': self.condition_name,
                'values': [[value_pattern.format(self=self)]],
            }
        elif self.type == 'zone':
            rule = {
                'condition_name': self.condition_name,
                'values': [
                    {
                        'name': zone_name.format(self=self),
                        'type': 'geonode',
                        'is_prioritized': False,
                    }
                    for zone_name in value_pattern.split(',')
                ],
            }
        elif self.type == 'integer':
            rule = {
                'condition_name': self.condition_name,
                'values': [int(value_pattern.format(self=self))],
            }
        elif self.type == 'bool':
            rule = {
                'condition_name': self.condition_name,
                'values': [int(value_pattern.format(self=self))],
            }
        elif self.type == 'double_range':
            rule = {
                'condition_name': self.condition_name,
                'values': [
                    {'type': 'double_range', 'start': '1', 'end': '1.1'},
                ],
            }
        elif self.type == 'int_range':
            rule = {
                'condition_name': self.condition_name,
                'values': [{'start': 1, 'end': 2}],
            }
        elif self.type == 'trips_restriction':
            rule = {
                'condition_name': self.condition_name,
                'values': [
                    {
                        'allowed_trips_count': {'start': 1, 'end': 2},
                        'brand': 'just_brand',
                        'payment_type': 'card',
                        'tariff_class': 'business',
                    },
                ],
            }
        else:
            raise TypeError(f'{self.type} not expected')

        if has_exclusions:
            if self.type == 'text':
                rule['exclusions'] = ['some_exclusion']
            elif self.type == 'array':
                rule['exclusions'] = [['some_exclusion']]
            elif self.type == 'zone':
                rule['exclusions'] = [
                    {
                        'name': 'some_zone',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ]
            elif self.type == 'integer':
                rule['exclusions'] = [0]
            elif self.type == 'bool':
                rule['exclusions'] = [0]
            elif self.type == 'double_range':
                rule['exclusions'] = [
                    {'type': 'double_range', 'start': '1.2', 'end': '1.3'},
                ]
            elif self.type == 'int_range':
                rule['exclusions'] = [{'start': 2, 'end': 3}]
            elif self.type == 'trips_restriction':
                rule['exclusions'] = [
                    {
                        'allowed_trips_count': {'start': 2, 'end': 3},
                        'brand': 'just_brand',
                        'payment_type': 'card',
                        'tariff_class': 'business',
                    },
                ]
            else:
                raise TypeError(f'{self.type} not expected')
        return rule

    def get_response(self, values_type: ValuesType, has_exclusions):
        if self.condition_name == 'active_period':
            return None
        if values_type is ValuesType.TYPE:
            if has_exclusions and not self.exclusions_for_type:
                return {
                    'code': 'Validation error',
                    'message': (
                        f'condition ({self.condition_name}) with type '
                        f'Type does not support exclusions'
                    ),
                }
            return None

        if values_type is ValuesType.ANY:
            if has_exclusions and not self.exclusions_for_any:
                return {
                    'code': 'Validation error',
                    'message': (
                        f'condition ({self.condition_name}) '
                        f'with type Any does not support exclusions'
                    ),
                }
            if not self.support_any:
                return {
                    'code': 'Validation error',
                    'message': (
                        f'condition ({self.condition_name}) '
                        f'does not support Any'
                    ),
                }
            return None
        if values_type is ValuesType.OTHER:
            if has_exclusions and not self.exclusions_for_other:
                return {
                    'code': 'Validation error',
                    'message': (
                        f'condition ({self.condition_name}) with type '
                        f'Other does not support exclusions'
                    ),
                }
            if not self.support_other:
                return {
                    'code': 'Validation error',
                    'message': (
                        f'condition ({self.condition_name}) '
                        f'does not support Other'
                    ),
                }
        return None


@pytest.fixture
def draft_id_is_uuid(service_name):
    return False


@pytest.fixture
def draft_id(service_name):
    return f'{service_name}_draft_id'


@pytest.fixture
def draft_headers(draft_id, headers):
    return {
        'X-YaTaxi-Draft-Author': 'user',
        'X-YaTaxi-Draft-Tickets': 'ticket-1,ticket-2',
        'X-YaTaxi-Draft-Approvals': 'approver',
        'X-YaTaxi-Draft-Id': draft_id,
        **headers,
    }


@pytest.fixture
def discounts_count(pgsql, service_name):
    def func(hierarchy_name: str) -> int:
        pg_cursor = pgsql[service_name].cursor()
        pg_cursor.execute(
            f"""SELECT COUNT(*)
                FROM {service_name}.match_rules_{hierarchy_name};""",
        )
        return list(pg_cursor)[0][0]

    return func


def parametrize_is_check(func):
    decorator = pytest.mark.parametrize(
        'is_check, additional_request_fields',
        (
            pytest.param(
                False,
                {'revisions': [], 'affected_discount_ids': []},
                id='add_rules',
            ),
            pytest.param(
                True,
                {'update_existing_discounts': True},
                id='add_rules_check_update_existing_discounts',
            ),
            pytest.param(
                True,
                {'update_existing_discounts': False},
                id='add_rules_check_not_update_existing_discounts',
            ),
        ),
    )
    return decorator(func)


def mark_now(func):
    decorator = pytest.mark.now('2019-01-01T00:00:00+00:00')
    return decorator(func)


def parametrize_add_rules(condition_descriptions: List[dict]):
    decorators = [
        pytest.mark.parametrize('has_exclusions', [True, False]),
        pytest.mark.parametrize('values_type', list(ValuesType)),
        pytest.mark.parametrize(
            'hierarchy_name, condition_name',
            [
                (description['name'], rule['condition_name'])
                for description in condition_descriptions
                for rule in description['conditions']
            ],
        ),
    ]

    def wrapper(func):
        for decorator in decorators:
            func = decorator(func)
        return mark_now(parametrize_is_check(func))

    return wrapper


@pytest.fixture
def get_condition_description(condition_descriptions):
    _all_descriptions: dict = {}

    for description in condition_descriptions:
        descriptions = _all_descriptions.setdefault(description['name'], {})
        for condition in description['conditions']:
            descriptions[condition['condition_name']] = ConditionDescription(
                **condition,
            )

    def func(hierarchy_name, condition_name) -> ConditionDescription:
        return _all_descriptions[hierarchy_name][condition_name]

    return func


@pytest.fixture
def check_add_rules_validation(
        client,
        pgsql,
        discounts_count,
        add_rules_url: str,
        add_rules_check_url: str,
        headers: dict,
        draft_headers: dict,
        default_discount: dict,
        draft_id_is_uuid: bool,
):
    async def func(
            is_check: str,
            additional_request_fields: dict,
            hierarchy_name: str,
            rules: List[dict],
            discount: dict = None,
            expected_status_code: int = 200,
            expected_response: Optional[dict] = None,
            expected_revisions_count: int = 0,
            expected_affected_discount_ids_count: int = 0,
            series_id: Optional[str] = None,
            custom_draft_id: Optional[str] = None,
    ):
        if series_id is None:
            series_id = SERIES_ID
        handler = add_rules_check_url if is_check else add_rules_url
        if discount is None:
            discount = default_discount
        headers = draft_headers.copy()
        headers['X-YaTaxi-Draft-Id'] = 'draft_id_check_add_rules_validation'
        if draft_id_is_uuid:
            headers['X-YaTaxi-Draft-Id'] = str(uuid.uuid4())
        if custom_draft_id:
            headers['X-YaTaxi-Draft-Id'] = custom_draft_id
        start_discounts_count = discounts_count(hierarchy_name)
        request: dict = {
            'rules': rules,
            'data': {'hierarchy_name': hierarchy_name, 'discount': discount},
            'series_id': series_id,
        }
        request.update(additional_request_fields)
        response = await client.post(handler, request, headers=headers)

        assert response.status_code == expected_status_code, response.text
        end_discounts_count = discounts_count(hierarchy_name)
        if expected_status_code == 200:
            if handler == add_rules_url:
                assert end_discounts_count != start_discounts_count
                assert not response.content or response.content == b'{}'
                return None
            response_json = response.json()
            revisions: List[int] = response_json['data'].pop('revisions', [])
            affected_discount_ids: List[str] = response_json['data'].pop(
                'affected_discount_ids', [],
            )
            assert len(revisions) == expected_revisions_count
            assert (
                len(affected_discount_ids)
                == expected_affected_discount_ids_count
            )
            data: dict = {'rules': request['rules'], 'data': request['data']}
            series_id_ = request.get('series_id')
            if (
                    additional_request_fields['update_existing_discounts']
                    is not None
            ):
                data['update_existing_discounts'] = additional_request_fields[
                    'update_existing_discounts'
                ]
            if series_id_ is not None:
                data['series_id'] = series_id_
            if not data['data']['discount'].get('active_with_surge'):
                data['data']['discount'].pop('active_with_surge', None)
            if not response_json['data']['data']['discount'].get(
                    'active_with_surge',
            ):
                response_json['data']['data']['discount'].pop(
                    'active_with_surge', None,
                )
            if revisions:
                lock_ids = [
                    {'custom': True, 'id': str(revision)}
                    for revision in revisions
                ]
            else:
                lock_ids = [
                    {
                        'custom': True,
                        'id': 'ride-discounts' + affected_discount_id,
                    }
                    for affected_discount_id in affected_discount_ids
                ]
            assert response_json == {'data': data, 'lock_ids': lock_ids}
            assert end_discounts_count == start_discounts_count
            return revisions if revisions else affected_discount_ids
        response_json = response.json()
        details = response_json.get('details')
        if details is not None:
            response_json.pop('details')
        if expected_response is not None:
            assert response_json == expected_response
        assert end_discounts_count == start_discounts_count
        return None

    return func


@pytest.fixture
def add_rules(client, check_add_rules_validation):
    async def func(
            add_rules_data: Dict[str, List[dict]],
            additional_request_fields: Optional[dict] = None,
    ):
        request_fields: dict = {'revisions': [], 'affected_discount_ids': []}
        if additional_request_fields is not None:
            request_fields.update(additional_request_fields)
        items = list(add_rules_data.items())
        items.sort()
        for hierarchy_name, data_items in items:
            for data in data_items:
                await check_add_rules_validation(
                    False,
                    request_fields,
                    hierarchy_name,
                    data['rules'],
                    data['discount'],
                    200,
                    None,
                    0,
                    0,
                    data.get('series_id'),
                )

    return func


@pytest.fixture
def additional_rules():
    return []


@pytest.fixture
async def check_add_rules(
        add_rules_check_url,
        add_rules_url,
        check_add_rules_validation,
        get_condition_description,
        additional_rules,
):
    async def func(
            hierarchy_name: str,
            condition_name: str,
            additional_request_fields,
            is_check,
            has_exclusions,
            values_type: ValuesType,
            discount=None,
            value_patterns: Mapping = types.MappingProxyType({}),
            active_period: Optional[dict] = None,
    ):
        additional_rules_ = {
            item['condition_name']: item for item in additional_rules
        }
        condition_description = get_condition_description(
            hierarchy_name, condition_name,
        )
        active_period_description = get_condition_description(
            hierarchy_name, 'active_period',
        )
        expected_response = condition_description.get_response(
            values_type, has_exclusions,
        )
        rules = [
            active_period_description.get_rule(
                values_type, has_exclusions, None, active_period,
            ),
        ]
        additional_rules_.pop(condition_name, None)

        if condition_name != 'active_period':
            value_pattern = value_patterns.get(
                condition_description.condition_name,
            )
            rules.append(
                condition_description.get_rule(
                    values_type, has_exclusions, value_pattern,
                ),
            )
        rules.extend(additional_rules_.values())
        await check_add_rules_validation(
            is_check,
            additional_request_fields,
            hierarchy_name,
            rules,
            discount,
            400 if expected_response else 200,
            expected_response,
            0,
            0,
            SERIES_ID,
        )

    return func
