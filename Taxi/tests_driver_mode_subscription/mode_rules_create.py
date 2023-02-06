import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

_DEFAULT_DRAFTS = [mode_rules.Draft('42', 'create')]

DEFAULT_BILLING_DRIVER_MODE_SETTINGS: Dict[str, Any] = {
    'some_billing_mode_rule': [],
}

_REQUEST_HEADER = {
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
    'X-Yandex-Login': 'test_user',
    'X-YaTaxi-Draft-Id': _DEFAULT_DRAFTS[0].draft_id,
}

DEFAULT_RULE_START_TIME = '2020-08-06T19:51:00+00:00'

DEFAULT_SCHEMA_VERSION = 1


class RuleData:
    def __init__(
            self,
            work_mode: str = 'test_rule',
            work_mode_class: Optional[str] = None,
            billing_mode: str = 'some_billing_mode',
            billing_mode_rule: str = 'some_billing_mode_rule',
            display_mode: str = 'orders_type',
            display_profile: str = 'all_features',
            features: Optional[List[Dict[str, Any]]] = None,
            starts_at: Optional[str] = DEFAULT_RULE_START_TIME,
            stops_at: Optional[str] = None,
            conditions: Optional[Dict[str, Any]] = None,
            offers_group: Optional[str] = 'taxi',
            drafts: List[mode_rules.Draft] = None,
            schema_version: Optional[int] = DEFAULT_SCHEMA_VERSION,
    ):
        self.work_mode = work_mode
        self.work_mode_class = work_mode_class
        self.billing_mode = billing_mode
        self.billing_mode_rule = billing_mode_rule
        self.display_mode = display_mode
        self.display_profile = display_profile
        self.features = features
        self.starts_at = starts_at
        self.stops_at = stops_at
        self.conditions = conditions
        self.offers_group = offers_group
        self.drafts = drafts if drafts else _DEFAULT_DRAFTS
        self.schema_version = schema_version

    def as_request(self, rules_to_close: Optional[List[str]] = None):
        result: Dict[str, Any] = {
            'rule': {
                'billing_settings': {
                    'mode': self.billing_mode,
                    'mode_rule': self.billing_mode_rule,
                },
                'display_settings': {
                    'mode': self.display_mode,
                    'profile': self.display_profile,
                },
                'starts_at': self.starts_at,
                'work_mode': self.work_mode,
            },
        }
        if self.work_mode_class:
            result['rule']['work_mode_class'] = self.work_mode_class
        if self.stops_at:
            result['rule']['stops_at'] = self.stops_at
        if self.offers_group:
            result['rule']['offers_group'] = self.offers_group
        if self.features:
            result['rule']['features'] = self.features
        if self.conditions:
            result['rule']['conditions'] = {'condition': self.conditions}

        if rules_to_close:
            result['rules_to_close'] = [
                {'rule_id': rule} for rule in rules_to_close
            ]

        if self.schema_version is not None:
            result['schema_version'] = self.schema_version

        return result

    def as_db_row(self):
        return (
            self.work_mode,
            self.work_mode_class,
            datetime.datetime.fromisoformat(self.starts_at).replace(
                tzinfo=None,
            ),
            datetime.datetime.fromisoformat(self.stops_at).replace(tzinfo=None)
            if self.stops_at
            else None,
            self.offers_group,
            {'condition': self.conditions} if self.conditions else None,
            self.display_mode,
            self.display_profile,
            self.billing_mode,
            self.billing_mode_rule,
            self.features,
            '{'
            + ','.join(
                [
                    f'"({draft.draft_id},{draft.action})"'
                    for draft in self.drafts
                ],
            )
            + '}',
            self.schema_version
            if self.schema_version is not None
            else DEFAULT_SCHEMA_VERSION,
        )


async def check_test_create_body_base(
        taxi_driver_mode_subscription,
        request_data: Dict[str, Any],
        expected_check_error_msg: Optional[str],
        expected_create_error_msg: Optional[str],
        expected_error_code: Optional[str] = 'INVALID_MODE_RULE',
        headers: Optional[Dict[str, str]] = None,
):
    if not headers:
        headers = _REQUEST_HEADER

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/check_create', json=request_data, headers=headers,
    )
    response_json = response.json()
    if expected_check_error_msg:
        assert response.status_code == 400

        assert response_json.pop('details')

        assert response_json == {
            'code': expected_error_code,
            'message': expected_check_error_msg,
        }
    else:
        assert response.status_code == 200

        assert response_json == {
            'data': request_data,
            'lock_ids': [
                {
                    'custom': True,
                    'id': mode_rules.build_draft_lock_id(
                        request_data['rule']['work_mode'],
                    ),
                },
            ],
        }

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/create', json=request_data, headers=headers,
    )
    response_json = response.json()
    if expected_create_error_msg:
        assert response.status_code == 400

        assert response_json.pop('details')

        assert response_json == {
            'code': expected_error_code,
            'message': expected_create_error_msg,
        }
    else:
        assert response.status_code == 200
        assert response_json == {}
