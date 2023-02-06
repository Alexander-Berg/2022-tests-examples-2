import copy
import dataclasses
import datetime
import hashlib
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

_MODE_RULE_ORDERS: Dict[str, Any] = {
    'starts_at': '1970-01-01T00:00:00-00:00',
    'settings': {
        'billing': {
            'mode': 'some_billing_mode',
            'mode_rule': 'some_billing_mode_rule',
        },
        'display_mode': 'orders_type',
        'offers_group': 'taxi',
    },
}

# Default DRIVER_MODE_RULES config value
_DEFAULT_MODE_RULES_CONFIG: Dict[str, List[Dict[str, Any]]] = {
    'driver_fix': [
        {
            'starts_at': '1970-01-01T00:00:00-00:00',
            'settings': {
                'offers_group': 'taxi',
                'billing': {
                    'mode': 'driver_fix',
                    'mode_rule': 'driver_fix_billing_mode_rule',
                },
                'display_mode': 'driver_fix_type',
                'features': {'driver_fix': {}},
            },
        },
    ],
    'orders': [_MODE_RULE_ORDERS],
    'custom_orders': [_MODE_RULE_ORDERS],
    'uberdriver': [
        {
            'starts_at': '1970-01-01T00:00:00-00:00',
            'settings': {
                'billing': {
                    'mode': 'uberdriver_billing_mode',
                    'mode_rule': 'uberdriver_billing_mode_rule',
                },
                'display_mode': 'uberdriver_type',
            },
        },
    ],
}

DEFAULT_BILLING_MODE = 'orders'
DEFAULT_BILLING_MODE_RULE = 'orders'
DEFAULT_DISPLAY_MODE = 'orders_type'


def default_mode_rules() -> Dict[str, List[Dict[str, Any]]]:
    return copy.deepcopy(_DEFAULT_MODE_RULES_CONFIG)


# Default mode used for any patch, based on 'orders' work mode
def _get_default_mode_rule() -> Dict[str, Any]:
    return _MODE_RULE_ORDERS


def get_mode_version(
        mode_rules: Dict[str, List[Dict[str, Any]]],
        mode_name: str,
        time_point: datetime.datetime,
) -> Optional[Dict[str, Any]]:
    assert mode_name in mode_rules

    versions = mode_rules[mode_name]
    for version in reversed(versions):
        starts_at = datetime.datetime.fromisoformat(version['starts_at'])
        if starts_at <= time_point:
            return version

    return None


# Extracts starts_at property from mode rule's version
def get_starts_at(version: Dict[str, Any]) -> datetime.datetime:
    return datetime.datetime.fromisoformat(version['starts_at'])


# Extracts starts_at property from rules config for given mode and time point
def find_starts_at(
        mode_rules: Dict[str, List[Dict[str, Any]]],
        mode_name: str,
        time_point: datetime.datetime,
) -> datetime.datetime:
    version = get_mode_version(mode_rules, mode_name, time_point)
    assert version

    return get_starts_at(version)


# Searches for active at time_point mode rule's display mode
def find_display_mode(
        mode_rules: Dict[str, List[Dict[str, Any]]],
        mode_name: str,
        time_point: datetime.datetime,
) -> str:
    version = get_mode_version(mode_rules, mode_name, time_point)
    assert version

    return version['settings']['display_mode']


@dataclasses.dataclass
class Draft:
    draft_id: str
    action: str


@dataclasses.dataclass
class ModeClass:
    name: str
    mode_names: List[str]


class Patch:
    def __init__(
            self,
            rule_name: str,
            billing_mode: Optional[str] = None,
            billing_mode_rule: Optional[str] = None,
            display_mode: Optional[str] = None,
            display_profile: Optional[str] = None,
            features: Optional[Dict[str, Any]] = None,
            assign_tags: Optional[List[str]] = None,
            starts_at: Optional[datetime.datetime] = None,
            stops_at: Optional[datetime.datetime] = None,
            clear_stops_at: Optional[bool] = None,
            condition: Optional[Dict[str, Any]] = None,
            offers_group: Optional[str] = None,
            rule_id: Optional[str] = None,
            is_canceled: Optional[bool] = None,
            drafts: Optional[List[Draft]] = None,
            schema_version: Optional[int] = None,
    ):
        self.rule_name = rule_name
        self.billing_mode = billing_mode
        self.billing_mode_rule = billing_mode_rule
        self.display_mode = display_mode
        self.display_profile = display_profile
        self.features = features
        self.assign_tags = assign_tags
        self.starts_at = starts_at
        self.stops_at = stops_at
        self.clear_stops_at = clear_stops_at
        self.condition = condition
        self.offers_group = offers_group
        self.rule_id = rule_id
        self.is_canceled = is_canceled
        self.drafts = drafts
        self.schema_version = schema_version

    def _patch_mode_rule(
            self, source_rule: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        rule = copy.deepcopy(source_rule or _get_default_mode_rule())
        settings = rule['settings']

        if self.billing_mode:
            settings['billing']['mode'] = self.billing_mode

        if self.billing_mode_rule:
            settings['billing']['mode_rule'] = self.billing_mode_rule

        if self.display_mode:
            settings['display_mode'] = self.display_mode

        if self.display_profile:
            settings['display_profile'] = self.display_profile

        if self.condition:
            settings['condition'] = self.condition

        if self.offers_group:
            settings['offers_group'] = self.offers_group

        if self.rule_id:
            settings['rule_id'] = self.rule_id

        if self.features:
            # excluding parameters
            assert self.assign_tags is None
            settings['features'] = {
                name: value for name, value in self.features.items()
            }
        elif self.assign_tags is not None:
            _features = settings.pop('features', {})
            if self.assign_tags:
                # you can only assign 1 or more tags in a feature
                _features['tags'] = {'assign': self.assign_tags}
            else:
                # remove tags if empty list was specified
                _features.pop('tags', {})
            settings['features'] = _features
        elif self.features is not None:
            # empty features passed should mean intention to remove existing
            settings.pop('features', {})

        if self.starts_at:
            rule['starts_at'] = self.starts_at.isoformat()

        if self.clear_stops_at:
            rule['stops_at'] = None

        if self.stops_at:
            rule['stops_at'] = self.stops_at.isoformat()

        if self.is_canceled:
            rule['is_canceled'] = self.is_canceled

        if self.drafts:
            rule['drafts'] = self.drafts

        if self.schema_version:
            rule['schema_version'] = self.schema_version

        return rule

    def apply(
            self, rules: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        source_rule = (
            rules[self.rule_name][-1]
            if (self.rule_name in rules)
            else _get_default_mode_rule()
        )

        patched_rule = self._patch_mode_rule(source_rule)

        if self.rule_name in rules:
            versions = rules[self.rule_name]
            assert versions

            if self.starts_at and self.starts_at != get_starts_at(
                    versions[-1],
            ):
                assert self.starts_at > get_starts_at(versions[-1])
                versions.append(patched_rule)
            else:
                # overriding default mode rule's previous version
                versions[-1] = patched_rule
        else:
            rules[self.rule_name] = [patched_rule]

        return rules


def patched_mode_rules(
        rule_name: str,
        rules: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        billing_mode: Optional[str] = None,
        billing_mode_rule: Optional[str] = None,
        display_mode: Optional[str] = None,
        display_profile: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        assign_tags: Optional[List[str]] = None,
        starts_at: Optional[datetime.datetime] = None,
        stops_at: Optional[datetime.datetime] = None,
        condition: Optional[Dict[str, Any]] = None,
        offers_group: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    if not rules:
        rules = default_mode_rules()

    patch = Patch(
        rule_name=rule_name,
        billing_mode=billing_mode,
        billing_mode_rule=billing_mode_rule,
        display_mode=display_mode,
        display_profile=display_profile,
        features=features,
        assign_tags=assign_tags,
        starts_at=starts_at,
        stops_at=stops_at,
        condition=condition,
        offers_group=offers_group,
    )

    return patch.apply(rules)


def patched(
        patches: List[Patch],
        rules: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    if rules is None:
        rules = default_mode_rules()

    for patch in patches:
        rules = patch.apply(rules)

    return rules


def init_admin_schema_version(version: int = 1):
    return f"""INSERT INTO config.admin_schemas_version(version, updated_at)
               VALUES({version}, now())"""


def update_admin_schema_version(version: int):
    return f"""UPDATE config.admin_schemas_version SET version = {version}"""


def make_insert_offers_groups_sql(offers_groups: Set[str]):
    return (
        'INSERT INTO config.offers_groups (name) VALUES '
        + ', '.join(f'(\'{name}\')' for name in offers_groups)
        + ' ON CONFLICT(name) DO NOTHING; '
    )


def make_insert_mode_classes_sql(mode_classes: Set[str]):
    return (
        'INSERT INTO config.mode_classes (name) VALUES '
        + ', '.join(f'(\'{name}\')' for name in mode_classes)
        + ' ON CONFLICT(name) DO NOTHING; '
    )


def make_insert_modes_sql(mode_names: Set[str], class_by_mode: Dict[str, str]):
    return (
        'INSERT INTO config.modes (name, class_id) VALUES '
        + ', '.join(
            f"""('{name}',
            (SELECT id FROM config.mode_classes mc
                       WHERE mc.name = '{class_by_mode.get(name, 'null')}'))"""
            for name in mode_names
        )
        + ' ON CONFLICT(name) DO NOTHING  ; '
    )


def _make_mode_rules_insert_sql(
        mode_names: Set[str],
        offers_groups: Set[str],
        conditions: List[Tuple[int, str]],
        rules_values: List[Any],
        mode_classes: Optional[List[ModeClass]],
):
    sql = 'DELETE FROM config.mode_rules; '

    class_by_mode: Dict[str, str] = {}

    if mode_classes:
        mode_classes_names: Set[str] = set()
        for mode_class in mode_classes:
            mode_classes_names.add(mode_class.name)
            for mode_name in mode_class.mode_names:
                class_by_mode[mode_name] = mode_class.name

        sql += make_insert_mode_classes_sql(mode_classes_names)

    sql += make_insert_modes_sql(mode_names, class_by_mode)

    sql += make_insert_offers_groups_sql(offers_groups)

    sql += 'DELETE FROM config.conditions; '
    # TODO: store condition and condition_id together
    if conditions:
        sql += (
            'INSERT INTO config.conditions (id, data) VALUES '
            + ', '.join(f'(\'{id}\',\'{data}\')' for id, data in conditions)
            + '; '
        )

    sql += (
        """INSERT INTO config.mode_rules(
           rule_id,
           mode_id,
           starts_at,
           stops_at,
           offers_group_id,
           display_mode,
           display_profile,
           billing_mode,
           billing_mode_rule,
           features,
           condition_id,
           canceled,
           drafts,
           admin_schemas_version
        ) VALUES """
        + ', '.join(rules_values)
        + ' ;'
    )

    return sql


def _make_mode_rules_insert_sql_values(
        rule_id: str,
        mode_name: str,
        starts_at: str,
        stops_at: Optional[str],
        offers_group: Optional[str],
        display_mode: str,
        display_profile: str,
        billing_mode: str,
        billing_mode_rule: str,
        features: Optional[List[Dict[str, Any]]],
        condition_id: Optional[int],
        is_canceled: bool,
        drafts: List[Draft],
        schema_version: int,
):
    return (
        (
            '(\'%s\', '  # rule_id
            '%s, '  # mode_id
            '\'%s\', '  # starts_at
            '%s, '  # stops_at
            '%s, '  # offers_group
            '\'%s\', '  # display_mode
            '\'%s\', '  # display_profile
            '\'%s\', '  # billing_mode
            '\'%s\','  # billing_mode_rule
            '%s, '  # features
            '%s, '  # conditions
            '%s, '  # canceled
            '\'{%s}\', '  # drafts
            '%d )'  # admin_schemas_version
        )
        % (
            rule_id,
            '(SELECT id FROM config.modes WHERE name = \'%s\')' % mode_name,
            starts_at,
            f'\'{stops_at}\'' if stops_at else 'Null',
            (
                '(SELECT id FROM config.offers_groups WHERE name = \'%s\')'
                % offers_group
            )
            if offers_group
            else 'Null',
            display_mode,
            display_profile,
            billing_mode,
            billing_mode_rule,
            f'\'{json.dumps(features)}\'' if features else 'Null',
            f'\'{condition_id}\'' if condition_id else 'Null',
            f'{is_canceled}',
            ','.join(
                [f'"({draft.draft_id},{draft.action})"' for draft in drafts],
            ),
            schema_version,
        )
    )


def patch_feature_settings(
        mode_name: str, feature_name: str, settings: Dict[str, Any],
):
    # for backward compability in db rules reposition profile required
    if feature_name == 'reposition':
        if 'profile' not in settings:
            settings['profile'] = mode_name


def _to_db(
        rules_cfg: Dict[str, List[Dict[str, Any]]],
        mode_classes: Optional[List[ModeClass]],
):
    rules_values: List[Any] = []
    offers_groups = set()
    conditions: List[Tuple[int, str]] = []
    for mode_name, rules in rules_cfg.items():
        rules_count = len(rules)
        for next_rule_idx, rule in enumerate(rules, start=1):
            starts_at: str = rule['starts_at']

            stops_at: Optional[str] = rule.get('stops_at')
            if not stops_at and next_rule_idx < rules_count:
                stops_at = rules[next_rule_idx].get('starts_at')

            display_mode = rule['settings']['display_mode']
            # TODO: remove fallback to work_mode
            display_profile = rule['settings'].get(
                'display_profile', mode_name,
            )

            billing_mode = rule['settings']['billing']['mode']
            billing_mode_rule = rule['settings']['billing']['mode_rule']

            features_cfg = rule['settings'].get('features', {})
            features = []
            for name, settings in features_cfg.items():
                _settings = settings.copy()
                patch_feature_settings(mode_name, name, _settings)

                features.append({'name': name, 'settings': _settings})

            offers_group = rule['settings'].get('offers_group')
            # For backward compability interpret 'no_group' as no offers_group
            if offers_group and offers_group != 'no_group':
                offers_groups.add(offers_group)

            rule_id = rule['settings'].get('rule_id')
            if not rule_id:
                hash_key = (mode_name + str(starts_at)).encode('utf-8')
                rule_id = hashlib.md5(hash_key).hexdigest()

            is_canceled = rule.get('is_canceled', False)

            condition_id: Optional[int] = None
            conditions_cfg = rule['settings'].get('condition')
            if conditions_cfg:
                condition_id = len(conditions) + 1
                condition_obj = {'condition': conditions_cfg}
                conditions.append((condition_id, json.dumps(condition_obj)))

            drafts = rule.get('drafts', [])

            default_schema_version = 1

            schema_version = rule.get('schema_version', default_schema_version)

            rules_values.append(
                _make_mode_rules_insert_sql_values(
                    rule_id,
                    mode_name,
                    starts_at,
                    stops_at,
                    offers_group,
                    display_mode,
                    display_profile,
                    billing_mode,
                    billing_mode_rule,
                    features,
                    condition_id,
                    is_canceled,
                    drafts,
                    schema_version,
                ),
            )

    return _make_mode_rules_insert_sql(
        set(rules_cfg.keys()),
        offers_groups,
        conditions,
        rules_values,
        mode_classes,
    )


def patched_db(
        patches: List[Patch],
        rules: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        mode_classes: Optional[List[ModeClass]] = None,
):
    return _to_db(patched(patches, rules), mode_classes)


def build_draft_lock_id(work_mode: str):
    return 'driver-mode-subscription:admin_mode_rules:' + work_mode
