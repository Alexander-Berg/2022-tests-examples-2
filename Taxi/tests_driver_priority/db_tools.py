import dataclasses
import datetime
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from tests_driver_priority import constants
from tests_driver_priority import logical_rules
from tests_driver_priority import priority_items
from tests_driver_priority import utils

MINUTE = datetime.timedelta(minutes=1)
HOUR = datetime.timedelta(hours=1)
DAY = datetime.timedelta(days=1)
TWO_DAYS = datetime.timedelta(days=2)
SIX_DAYS = datetime.timedelta(days=6)
WEEK = datetime.timedelta(days=7)

DEFAULT_ACHIEVED_PAYLOAD = {
    'main_title': 'some_title',
    'constructor': [{'numbered_list': [{'title': 'some_title'}]}],
}

DEFAULT_PAYLOADS = {'achieved': DEFAULT_ACHIEVED_PAYLOAD}


def remove_nullable_keys(some_dict: Dict[str, Any]):
    return {k: v for k, v in some_dict.items() if v is not None}


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


DEFAULT_PRIORITY_RULES = [
    logical_rules.TagRule('silver', logical_rules.PriorityValue(-3, -3), None),
    logical_rules.TagRule(
        'platinum', logical_rules.PriorityValue(-2, -2), None,
    ),
    logical_rules.RatingRule(
        remove_nullable_keys(
            dataclasses.asdict(logical_rules.RatingValue(4.8, 4.9)),
        ),
        logical_rules.PriorityValue(-1, -1),
        'rating',
        None,
    ),
    logical_rules.RatingRule(
        remove_nullable_keys(
            dataclasses.asdict(logical_rules.RatingValue(1.0, None)),
        ),
        logical_rules.PriorityValue(0, 0),
        'rating',
        None,
    ),
    logical_rules.RatingRule(
        remove_nullable_keys(
            dataclasses.asdict(logical_rules.RatingValue(None, 5.0)),
        ),
        logical_rules.PriorityValue(-1, 1),
        'rating',
        None,
    ),
    logical_rules.CarYearRule(
        remove_nullable_keys(
            dataclasses.asdict(logical_rules.CarYear(True, 2019)),
        ),
        logical_rules.PriorityValue(-2, 1),
        'car_year',
        None,
    ),
]

DEFAULT_RULE = {
    'ranked_rule': [
        remove_nullable_keys(dataclasses.asdict(rule))
        for rule in DEFAULT_PRIORITY_RULES
    ],
}

WRONG_TOPIC_RULE = {
    'single_rule': {
        'tag_name': 'gold',  # tag doesn't have relation with priority topic
        'priority_value': {'backend': 5, 'display': 5},
    },
}

WRONG_VALUES_RANKED_RULE = {
    'ranked_rule': [
        remove_nullable_keys(dataclasses.asdict(rule))
        for rule in [
            logical_rules.TagRule(
                'platinum', logical_rules.PriorityValue(-5, -5), None,
            ),
            logical_rules.TagRule(
                'platinum', logical_rules.PriorityValue(-3, 3), None,
            ),
            logical_rules.TagRule(
                'silver', logical_rules.PriorityValue(-1, 3), None,
            ),
            logical_rules.TagRule(
                'silver', logical_rules.PriorityValue(-3, 1), None,
            ),
        ]
    ],
}

WRONG_VALUES_EXCLUDING_RULE = {
    'excluding_rule': [
        remove_nullable_keys(dataclasses.asdict(rule))
        for rule in [
            logical_rules.TagRule(
                'platinum', logical_rules.PriorityValue(3, -1), None,
            ),
            logical_rules.TagRule(
                'platinum', logical_rules.PriorityValue(5, -2), None,
            ),
            logical_rules.TagRule(
                'silver', logical_rules.PriorityValue(2, -1), None,
            ),
        ]
    ],
}

ACTIVITY_RULE = {'tanker_keys_prefix': 'activity', 'activity_levels': {}}


def make_tag_rule(
        tag_name: str,
        backend: int,
        display: Optional[int] = None,
        override: Optional[Dict[str, Any]] = None,
):
    tag_rule = {
        'tag_name': tag_name,
        'priority_value': {'backend': backend, 'display': display or backend},
    }
    if override is not None:
        tag_rule['override'] = override
    return tag_rule


def insert_priority(
        id_: int,
        name: str,
        is_enabled: bool,
        tanker_keys_prefix: str,
        can_contain_activity_rule: bool = False,
) -> str:
    return (
        f'INSERT INTO state.priorities (id, name, is_enabled, '
        f'tanker_keys_prefix, description, can_contain_activity_rule) VALUES '
        f'({id_}, \'{name}\', {is_enabled}, \'{tanker_keys_prefix}\', '
        f'\'description\', {can_contain_activity_rule})'
    )


def insert_priority_relation(
        agglomeration: str, priority_id: int, is_excluded: bool,
) -> str:
    return (
        f'INSERT INTO state.priorities_relations VALUES '
        f'(\'{agglomeration}\', {priority_id}, {is_excluded})'
    )


def insert_preset(
        id_: int,
        priority_id: int,
        name: str,
        created_at: datetime.datetime,
        is_default: bool = False,
) -> str:
    return (
        f'INSERT INTO state.presets VALUES ({id_}, {priority_id}, '
        f'\'{name}\', \'{created_at}\'::timestamptz, {is_default}, '
        f'\'description\')'
    )


def insert_preset_relation(agglomeration: str, preset_id: int) -> str:
    return (
        f'INSERT INTO state.presets_relations VALUES '
        f'(\'{agglomeration}\', {preset_id})'
    )


def insert_version(
        id_: int,
        preset_id: int,
        sort_order: int,
        rule: Dict[str, Any],
        achieved_payload: Dict[str, Any],
        created_at: datetime.datetime,
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime] = None,
        temporary_condition: Optional[Dict[str, Any]] = None,
        disabled_condition: Optional[Dict[str, Any]] = None,
        achievable_condition: Optional[Dict[str, Any]] = None,
        achievable_payload: Optional[Dict[str, Any]] = None,
) -> str:
    json_data = []
    for value in [
            rule,
            temporary_condition,
            disabled_condition,
            achievable_condition,
            achieved_payload,
            achievable_payload,
    ]:
        json_data.append(f'\'{json.dumps(value or dict())}\'::jsonb')

    raw_jsons = ', '.join(json_data)
    stops_at_value = 'NULL' if stops_at is None else f'\'{stops_at}\''
    return (
        f'INSERT INTO state.preset_versions VALUES ({id_}, {preset_id}, '
        f'{sort_order}, \'{created_at}\'::timestamptz, {raw_jsons}, '
        f'\'{starts_at}\'::timestamptz, '
        f'{stops_at_value}::timestamptz)'
    )


def insert_experiment(
        id_: int,
        priority_id: int,
        name: str,
        created_at: datetime.datetime,
        description: Optional[str],
) -> str:
    description_text = 'NULL' if description is None else f'\'{description}\''
    return (
        f'INSERT INTO state.experiments (id, priority_id, name, created_at, '
        f'description) VALUES ({id_}, {priority_id}, \'{name}\', '
        f'\'{created_at}\'::timestamptz, {description_text})'
    )


def insert_experiment_relation(agglomeration: str, experiment_id: int) -> str:
    return (
        f'INSERT INTO state.experiments_relations VALUES '
        f'(\'{agglomeration}\', {experiment_id})'
    )


def update_version_start_stop_time(
        version_id: int,
        starts_at: Optional[datetime.datetime] = None,
        stops_at: Optional[datetime.datetime] = None,
) -> str:
    set_parts = []
    if starts_at is not None:
        set_parts.append(f'starts_at=\'{starts_at}\'')
    if stops_at is not None:
        set_parts.append(f'stops_at=\'{stops_at}\'')
    return (
        f'UPDATE state.preset_versions SET {",".join(set_parts)} WHERE '
        f'id={version_id}'
    )


def get_priority_item_insertions(
        priority_id: int,
        preset_id: int,
        version_id: int,
        item: priority_items.Item,
) -> List[str]:
    return [
        insert_preset(
            priority_id,
            preset_id,
            item.preset.name,
            item.version.created_at,
            False,
        ),
        insert_version(
            version_id,
            preset_id,
            item.version.sort_order,
            item.rule,
            item.payloads['achieved'],
            item.version.created_at,
            item.version.starts_at,
            item.version.stops_at,
            item.conditions.temporary,
            item.conditions.disabled,
            item.conditions.achievable,
            item.payloads.get('achievable'),
        ),
    ]


def select_named(query: str, db):
    cursor = db.conn.cursor()
    cursor.execute(query)
    res: List[Dict[str, Any]] = []
    for row in cursor.fetchall():
        res.append({})
        last = len(res) - 1
        for pos in range(len(cursor.description)):
            res[last][cursor.description[pos][0]] = row[pos]
    return res


def _insert_version(
        id_: int,
        preset_id: int,
        sort_order: int,
        now: datetime.datetime,
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime] = None,
        achievable_condition: Optional[Any] = None,
        temporary_condition: Optional[Any] = None,
        disabled_condition: Optional[Any] = None,
) -> str:
    created_at = min(now, starts_at)
    return insert_version(
        id_,
        preset_id,
        sort_order,
        DEFAULT_RULE,
        DEFAULT_ACHIEVED_PAYLOAD,
        created_at,
        starts_at,
        stops_at=stops_at,
        temporary_condition=temporary_condition,
        achievable_condition=achievable_condition,
        disabled_condition=disabled_condition,
    )


def get_sequence_ids_update_queries() -> List[str]:
    table_names = ['priorities', 'presets', 'preset_versions']
    result = []
    for table_name in table_names:
        query = (
            f'SELECT setval(\'state.{table_name}_id_seq\', max_id) FROM '
            f'(SELECT max(id) max_id FROM state.{table_name}) subquery;'
        )
        result.append(query)
    return result


def join_queries(queries: List[str]) -> List[str]:
    return [';'.join(queries)]


def get_pg_default_data(now: datetime.datetime) -> List[str]:
    queries = [
        insert_priority(0, 'branding', True, 'branding'),
        insert_priority(1, 'loyalty', True, 'loyalty'),
        insert_priority(2, 'disabled', False, 'disabled'),
        insert_priority(3, 'empty_relations', False, 'empty_relations'),
        insert_priority_relation(constants.MSK, 0, False),
        insert_priority_relation(constants.TULA, 0, True),
        insert_priority_relation(constants.SPB, 0, True),
        insert_priority_relation(constants.SPB, 1, False),
        insert_priority_relation(constants.SPB, 2, True),
        insert_priority_relation(constants.BR_ROOT, 2, False),
        # make some experiments data
        insert_experiment(0, 0, 'exp0', now, None),
        insert_experiment(1, 0, 'exp1', now, 'spb exp'),
        insert_experiment(2, 1, 'exp2', now, 'loyalty_exp'),
        insert_experiment_relation('br_root', 0),
        insert_experiment_relation('br_moscow', 0),
        insert_experiment_relation('br_spb', 1),
        insert_experiment_relation('spb', 2),
        # presets 0 and 3 are default => cannot have relations
        insert_preset(0, 0, 'default', now, is_default=True),
        insert_preset(1, 0, 'actual_preset', now),
        insert_preset(2, 0, 'preset2', now),
        insert_preset(3, 1, 'default', now, is_default=True),
        insert_preset(4, 1, 'outdated_preset', now),
        insert_preset(5, 2, 'default', now, is_default=True),
        insert_preset(6, 3, 'default', now, is_default=True),
        insert_preset(7, 1, 'without_versions', now),
        insert_preset(8, 1, 'actual_preset', now - DAY),
        insert_preset_relation(constants.MSK, 1),
        insert_preset_relation(constants.SPB, 4),
        # presets 0, 3, 5 should have active version without ends_at
        _insert_version(0, 0, 0, now, now, stops_at=now + DAY),
        _insert_version(1, 0, 0, now, now + DAY),
        _insert_version(2, 1, 0, now, now, stops_at=now + HOUR),
        _insert_version(3, 1, 1, now, now + HOUR),
        _insert_version(4, 2, 1, now, now + HOUR, stops_at=now + DAY),
        _insert_version(
            5,
            3,
            1,
            now,
            now - DAY,
            temporary_condition={'value': True},
            achievable_condition={'value': False},
        ),
        _insert_version(6, 4, 1, now - DAY, now - DAY, stops_at=now - HOUR),
        _insert_version(7, 5, 2, now, now),
        _insert_version(8, 6, 3, now, now + HOUR, now + DAY),
        _insert_version(9, 6, 3, now, now + DAY, now + WEEK),
        _insert_version(10, 6, 3, now, now + WEEK),
        _insert_version(11, 8, 3, now - DAY, now - DAY, stops_at=now + DAY),
        _insert_version(12, 8, 3, now - DAY, now + DAY),
    ]

    # priority and default preset creation should be in single transaction, so
    # multiple queries should be joined in one
    return join_queries(queries) + get_sequence_ids_update_queries()


def select_priorities_info(db):
    query = (
        'SELECT name, is_enabled, tanker_keys_prefix, description '
        'FROM state.priorities'
    )
    result = {row.pop('name'): row for row in select_named(query, db)}

    query = (
        'SELECT priorities.name AS priority_name, agglomeration, is_excluded '
        'FROM state.priorities_relations '
        'INNER JOIN state.priorities AS priorities '
        'ON priorities.id = state.priorities_relations.priority_id'
    )
    for row in select_named(query, db):
        result[row['priority_name']].setdefault('agglomerations', {})[
            row['agglomeration']
        ] = row['is_excluded']

    query = (
        'SELECT priorities.name AS priority_name, presets.id, '
        'presets.name, presets.is_default, presets.description '
        'FROM state.presets AS presets '
        'INNER JOIN state.priorities AS priorities '
        'ON priorities.id = presets.priority_id'
    )
    presets_by_ids = {row.pop('id'): row for row in select_named(query, db)}

    query = (
        'SELECT preset_id, agglomeration FROM state.presets_relations '
        'ORDER BY agglomeration'
    )
    for row in select_named(query, db):
        presets_by_ids[row.pop('preset_id')].setdefault(
            'agglomerations', [],
        ).append(row['agglomeration'])

    query = (
        'SELECT preset_id, sort_order, rule, temporary_condition, '
        'disabled_condition, achievable_condition, achieved_payload, '
        'achievable_payload, created_at, starts_at, stops_at '
        'FROM state.preset_versions '
        'ORDER BY starts_at'
    )
    for row in select_named(query, db):
        row = remove_nullable_keys(row)
        presets_by_ids[row.pop('preset_id')].setdefault('versions', []).append(
            row,
        )

    for preset in presets_by_ids.values():
        preset = remove_nullable_keys(preset)
        result[preset.pop('priority_name')].setdefault('presets', {})[
            preset.pop('name')
        ] = preset

    return result


def get_priority_fields(priority_name: str, db) -> Dict[str, Any]:
    query = (
        f'SELECT is_enabled AS status, description, tanker_keys_prefix FROM '
        f'state.priorities WHERE name = \'{priority_name}\''
    )
    data = select_named(query, db)[0]
    status = 'active' if data['status'] else 'disabled'
    data['status'] = status
    return data


def get_priority_relations(priority_name: str, db) -> Dict[str, List[str]]:
    query = (
        f'SELECT agglomeration, is_excluded FROM state.priorities_relations '
        f'WHERE priority_id IN (SELECT id FROM state.priorities WHERE name=\''
        f'{priority_name}\') ORDER BY agglomeration'
    )
    rows = select_named(query, db)
    return {
        'enabled_in': [
            row['agglomeration'] for row in rows if not row['is_excluded']
        ],
        'disabled_in': [
            row['agglomeration'] for row in rows if row['is_excluded']
        ],
    }


def get_priority_presets_relations(
        priority_name: str, db,
) -> List[Dict[str, Any]]:
    query = (
        f'SELECT presets.name as name, presets.description, ARRAY(SELECT '
        f'agglomeration FROM state.presets_relations WHERE preset_id = '
        f'presets.id ORDER BY agglomeration) as agglomerations FROM '
        f'state.presets WHERE priority_id IN (SELECT id FROM state.priorities '
        f'WHERE name = \'{priority_name}\') '
        f'ORDER BY presets.is_default DESC, presets.name'
    )
    return select_named(query, db)


def get_preset_version(version_id: int, db) -> Optional[Dict[str, Any]]:
    query = (
        f'SELECT preset_id, sort_order, rule, temporary_condition, '
        f'disabled_condition, achievable_condition, achieved_payload, '
        f'achievable_payload, created_at, starts_at, stops_at '
        f'FROM state.preset_versions '
        f'WHERE id = {version_id}'
    )
    rows = select_named(query, db)

    assert 0 <= len(rows) <= 1
    return remove_nullable_keys(rows[0]) if rows else None


def get_preset_id(version_id: int, db) -> Optional[int]:
    query = (
        f'SELECT preset_id FROM state.preset_versions WHERE id = {version_id}'
    )
    rows = select_named(query, db)

    assert 0 <= len(rows) <= 1
    if rows:
        return rows[0]['preset_id']
    return None


def check_recalculation_task(
        db,
        expected_agglomerations: Optional[List[str]],
        expected_last_processed_timestamp: Optional[datetime.datetime] = None,
):
    query = (
        f'SELECT id, created_at, agglomerations, last_processed_timestamp '
        f'FROM service.recalculation_tasks'
    )
    rows = select_named(query, db)
    if expected_agglomerations is None:
        assert not rows, rows
    else:
        task = rows[0]
        assert 'created_at' in task
        assert (
            task['last_processed_timestamp']
            == expected_last_processed_timestamp
        )
        assert sorted(task['agglomerations']) == expected_agglomerations


def insert_priority_calculations(
        data: List[Tuple[str, str, datetime.datetime, datetime.datetime]],
) -> str:
    values = []
    for (dbid_uuid, tariff_zone, updated_at, last_login_at) in data:
        updated_at = utils.add_local_tz(updated_at)
        last_login_at = utils.add_local_tz(last_login_at)
        values.append(
            f"""
            ('{dbid_uuid}', '{tariff_zone}', 12345, '{updated_at}'::
            timestamptz, '{last_login_at}'::timestamptz)
            """,
        )
    values_str = ','.join(values)
    return (
        f'INSERT INTO service.last_priority_calculations (dbid_uuid, '
        f'tariff_zone, calculation_hash, updated_at, last_login_at) '
        f'VALUES {values_str};'
    )


def get_priority_experiments(priority_name: str, db):
    query = (
        f'SELECT experiments.name, experiments.description, ARRAY(SELECT '
        f'agglomeration FROM state.experiments_relations WHERE experiment_id='
        f'experiments.id ORDER BY agglomeration) as agglomerations FROM '
        f'state.experiments WHERE priority_id IN (SELECT id FROM '
        f'state.priorities WHERE name = \'{priority_name}\') '
        f'ORDER BY experiments.name'
    )
    return select_named(query, db)
