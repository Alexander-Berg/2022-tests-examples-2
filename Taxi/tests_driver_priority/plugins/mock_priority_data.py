import copy
import datetime
import enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from tests_driver_priority import db_tools

# Usage: @pytest.mark.priority_data(
#            now: datetime.datetime,
#            data: List[PriorityData],
#        )
_PRIORITY_DATA_MARKER = 'priority_data'
_DB_SERVICE_NAME = 'driver_priority'

_TYPE_INDEX = 0
_VALUE_INDEX = 1
_PRIORITY_INDEX = 2
_OVERRIDE_INDEX = 3

EMPTY_RULE = {
    'single_rule': {
        'tag_name': '',
        'priority_value': {'backend': 0, 'display': 0},
    },
}

EMPTY_PAYLOAD = {
    'main_title': '',
    'constructor': [
        {
            'title': '',
            'text': '',
            'numbered_list': [{'title': '', 'subtitle': ''}],
        },
    ],
}


class PriorityRuleType(enum.Enum):
    Single = 0
    Ranked = 1
    Excluded = 2
    Activity = 3


class RuleType(enum.Enum):
    TagRule = 0
    RatingRule = 1
    CarYearRule = 2
    ActivityRule = 3


class PriorityRule:
    def __init__(
            self,
            rule_type: PriorityRuleType,
            rules: List[
                Tuple[
                    RuleType,
                    Union[
                        str, Tuple[float, float, str], Tuple[bool, int, str],
                    ],
                    Optional[int],
                    Optional[Any],
                ]
            ],
    ):
        assert (
            (rule_type == PriorityRuleType.Single and len(rules) == 1)
            or (rule_type == PriorityRuleType.Ranked and len(rules) >= 2)
            or (rule_type == PriorityRuleType.Excluded and len(rules) >= 2)
            or (rule_type == PriorityRuleType.Activity and len(rules) == 1)
        )
        self.rule_type = rule_type
        self.rules = rules


class PriorityPayload:
    def __init__(
            self,
            achieved: Dict[str, Any],
            achievable: Optional[Dict[str, Any]] = None,
    ):
        self.achieved = achieved
        self.achievable = achievable


class PrioritySettings:
    def __init__(
            self,
            geo_nodes: List[str],
            sort_order: int,
            rule: PriorityRule,
            payload: PriorityPayload,
            is_temporary: Optional[Any] = None,
            is_achievable: Optional[Any] = None,
            is_disabled: Optional[Any] = None,
    ):
        self.geo_nodes = geo_nodes
        self.sort_order = sort_order
        self.rule = rule
        self.payload = payload
        self.is_achievable = is_achievable
        self.is_temporary = is_temporary
        self.is_disabled = is_disabled


class PriorityData:
    def __init__(
            self,
            name: str,
            settings: List[PrioritySettings],
            extra_geo_nodes: Optional[List[str]] = None,
            tanker_keys_prefix=None,
    ):
        self.name = name
        self.settings = settings
        self.extra_geo_nodes = extra_geo_nodes or []
        self.tanker_keys_prefix = tanker_keys_prefix or name


class PriorityDataContext:
    def __init__(self, pgsql):
        self.pgsql = pgsql

    def reset(self):
        pass

    def _make_rule(self, rule: PriorityRule) -> Dict[str, Any]:
        data = []
        for rule_item in rule.rules:
            item: Dict[str, Any] = {
                'priority_value': {
                    'backend': rule_item[_PRIORITY_INDEX],
                    'display': rule_item[_PRIORITY_INDEX],
                },
            }
            value = rule_item[_VALUE_INDEX]
            if rule_item[_TYPE_INDEX] == RuleType.TagRule:
                assert isinstance(value, str)
                item['tag_name'] = value
            elif rule_item[_TYPE_INDEX] == RuleType.RatingRule:
                assert isinstance(value, tuple)
                item['rating'] = {
                    'lower_bound': float(value[0]),
                    'upper_bound': float(value[1]),
                }
                item['tanker_key_part'] = str(value[2])
            elif rule_item[_TYPE_INDEX] == RuleType.CarYearRule:
                assert isinstance(value, tuple)
                key = 'higher_than' if value[0] else 'lower_than'
                item['car_year'] = {key: int(value[1])}
                item['tanker_key_part'] = str(value[2])
            else:  # rule_item[_TYPE_INDEX] == RuleType.ActivityRule:
                assert isinstance(value, str)
                item['tanker_key_part'] = str(value[2])
            if rule_item[_OVERRIDE_INDEX] is not None:
                item['override'] = rule_item[_OVERRIDE_INDEX]
            data.append(item)

        rule_data: Dict[str, Any] = {}
        if rule.rule_type == PriorityRuleType.Single:
            rule_data = {'single_rule': data[0]}
        elif rule.rule_type == PriorityRuleType.Ranked:
            rule_data = {'ranked_rule': data}
        elif rule.rule_type == PriorityRuleType.Excluded:
            rule_data = {'excluding_rule': data}
        elif rule.rule_type == PriorityRuleType.Activity:
            rule_data = {
                'activity_levels': {},
                'tanker_keys_prefix': data[0]['tanker_key_part'],
            }

        return rule_data

    def _make_condition(
            self, condition: Optional[Any],
    ) -> Optional[Dict[str, Any]]:
        if condition is None:
            return None
        if isinstance(condition, bool):
            return {'value': condition}
        return condition

    def _make_db_data(self, data: List[PriorityData], now) -> List[str]:
        priority_index = 0
        preset_index = 0
        version_index = 0
        queries = []

        for item in data:
            priority_index += 1
            queries.append(
                db_tools.insert_priority(
                    priority_index, item.name, True, item.tanker_keys_prefix,
                ),
            )

            # add priority relations
            priority_relations = copy.deepcopy(item.extra_geo_nodes)
            for settings in item.settings:
                priority_relations += settings.geo_nodes
            if ('__default__' in priority_relations) and (
                    'br_root' in priority_relations
            ):
                priority_relations.remove('__default__')
            for geo_node in priority_relations:
                queries.append(
                    db_tools.insert_priority_relation(
                        geo_node if geo_node != '__default__' else 'br_root',
                        priority_index,
                        False,
                    ),
                )

            default_settings = PrioritySettings(
                [],
                0,
                PriorityRule(
                    PriorityRuleType.Single, [(RuleType.TagRule, '', 0, None)],
                ),
                PriorityPayload(EMPTY_PAYLOAD),
                is_disabled=True,
            )

            for settings in item.settings:
                for geo_node in settings.geo_nodes:
                    if geo_node == '__default__':
                        default_settings = settings

                preset_relations = [
                    geo_node
                    for geo_node in settings.geo_nodes
                    if geo_node != '__default__'
                ]
                if preset_relations:
                    preset_index += 1
                    queries.append(
                        db_tools.insert_preset(
                            preset_index,
                            priority_index,
                            'preset' + str(preset_index),
                            now,
                        ),
                    )
                    for preset_relation in preset_relations:
                        queries.append(
                            db_tools.insert_preset_relation(
                                preset_relation, preset_index,
                            ),
                        )

                    version_index += 1
                    queries.append(
                        db_tools.insert_version(
                            version_index,
                            preset_index,
                            settings.sort_order,
                            self._make_rule(settings.rule),
                            settings.payload.achieved,
                            now,
                            now,
                            temporary_condition=self._make_condition(
                                settings.is_temporary,
                            ),
                            disabled_condition=self._make_condition(
                                settings.is_disabled,
                            ),
                            achievable_condition=self._make_condition(
                                settings.is_achievable,
                            ),
                            achievable_payload=settings.payload.achievable,
                        ),
                    )

            preset_index += 1
            queries.append(
                db_tools.insert_preset(
                    preset_index,
                    priority_index,
                    'default' + str(preset_index),
                    now,
                    is_default=True,
                ),
            )

            version_index += 1
            queries.append(
                db_tools.insert_version(
                    version_index,
                    preset_index,
                    default_settings.sort_order,
                    self._make_rule(default_settings.rule),
                    default_settings.payload.achieved,
                    now,
                    now,
                    temporary_condition=self._make_condition(
                        default_settings.is_temporary,
                    ),
                    disabled_condition=self._make_condition(
                        default_settings.is_disabled,
                    ),
                    achievable_condition=self._make_condition(
                        default_settings.is_achievable,
                    ),
                    achievable_payload=default_settings.payload.achievable,
                ),
            )

        return db_tools.join_queries(queries)

    def set_priority_data(
            self, now: datetime.datetime, data: List[PriorityData],
    ):
        self.pgsql[_DB_SERVICE_NAME].apply_queries(
            self._make_db_data(data, now),
        )


@pytest.fixture(name='priority_data', autouse=False)
def priority_data(pgsql):
    return PriorityDataContext(pgsql)


@pytest.fixture(name='priority_data_fixture', autouse=True)
def _priority_data_fixture(priority_data, request):  # pylint: disable=W0621,
    marker = request.node.get_closest_marker(_PRIORITY_DATA_MARKER)
    if marker:
        priority_data.set_priority_data(**marker.kwargs)

    yield priority_data


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_PRIORITY_DATA_MARKER}: set priority data',
    )
