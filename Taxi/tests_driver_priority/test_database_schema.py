import datetime
from typing import Optional

import psycopg2
import pytest
import pytz

from tests_driver_priority import constants
from tests_driver_priority import db_tools


NOW = datetime.datetime.now(pytz.timezone('UTC'))
HOUR = datetime.timedelta(hours=1)
DAY = datetime.timedelta(days=1)
WEEK = datetime.timedelta(days=7)


def _insert_version(
        id_: int,
        preset_id: int,
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime] = None,
) -> str:
    created_at = min(NOW, starts_at)
    return db_tools.insert_version(
        id_,
        preset_id,
        0,
        dict(),
        dict(),
        created_at,
        starts_at,
        stops_at=stops_at,
    )


@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            db_tools.insert_priority(0, 'priority_name', True, 'tk'),
            db_tools.insert_priority(1, 'empty_priority', True, 'tk'),
            db_tools.insert_priority(2, 'disabled_priority', False, 'tk'),
            db_tools.insert_priority(3, 'empty_relations', False, 'tk'),
            db_tools.insert_priority_relation(constants.MSK, 0, False),
            db_tools.insert_priority_relation(constants.BR_ROOT, 0, False),
            db_tools.insert_priority_relation(constants.SPB, 1, False),
            db_tools.insert_priority_relation(constants.SPB, 2, True),
            db_tools.insert_priority_relation(constants.BR_ROOT, 2, False),
            db_tools.insert_experiment(0, 0, 'first_exp', NOW, None),
            db_tools.insert_experiment(1, 0, 'second_exp', NOW, None),
            db_tools.insert_experiment(2, 1, 'exp_name', NOW, 'description'),
            db_tools.insert_experiment(
                3, 2, 'no_relation_exp', NOW, 'no relation exp',
            ),
            db_tools.insert_experiment_relation(constants.MSK, 0),
            db_tools.insert_experiment_relation(constants.SPB, 0),
            db_tools.insert_experiment_relation(constants.TULA, 1),
            db_tools.insert_experiment_relation(constants.MSK, 2),
            db_tools.insert_experiment_relation(constants.SPB, 2),
            # presets 0 and 3 are default => cannot have relations
            db_tools.insert_preset(0, 0, 'preset0', NOW, is_default=True),
            db_tools.insert_preset(1, 0, 'preset1', NOW),
            db_tools.insert_preset(2, 0, 'preset2', NOW),
            db_tools.insert_preset(3, 1, 'preset3', NOW, is_default=True),
            db_tools.insert_preset(4, 1, 'preset4', NOW),
            db_tools.insert_preset(5, 2, 'preset5', NOW, is_default=True),
            db_tools.insert_preset(6, 3, 'preset6', NOW, is_default=True),
            db_tools.insert_preset_relation(constants.MSK, 1),
            _insert_version(0, 0, NOW, stops_at=NOW + DAY),
            _insert_version(1, 0, NOW + DAY),
            _insert_version(2, 1, NOW, stops_at=NOW + HOUR),
            _insert_version(3, 1, NOW + DAY),
            _insert_version(4, 3, NOW + DAY),
            _insert_version(5, 5, NOW),
            _insert_version(6, 6, NOW),
            # empty duration, TODO: allow this?
            _insert_version(7, 2, NOW + HOUR, stops_at=NOW + HOUR),
            _insert_version(8, 3, NOW - DAY, stops_at=NOW),
            _insert_version(9, 4, NOW - DAY, stops_at=NOW - HOUR),
        ],
    ),
)
def test_version_agglomerations_constraint(pgsql):
    cursor = pgsql['driver_priority'].cursor()

    # test no default preset for priority
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_priority(4, 'new_priority', True, 'tk'))

    # test multi default presets for priority
    with pytest.raises(psycopg2.DatabaseError):
        queries = [
            db_tools.insert_preset(
                7, 0, 'default_preset', NOW, is_default=True,
            ),
            _insert_version(10, 7, NOW),
        ]
        cursor.execute(';'.join(queries))

    # test no version for default preset
    with pytest.raises(psycopg2.DatabaseError):
        queries = [
            db_tools.insert_priority(4, 'new_priority', True, 'tk'),
            db_tools.insert_preset(
                7, 4, 'default_preset', NOW, is_default=True,
            ),
        ]
        cursor.execute(';'.join(queries))

    # test no inf version for default preset (insert)
    with pytest.raises(psycopg2.DatabaseError):
        queries = [
            db_tools.insert_priority(4, 'new_priority', True, 'tk'),
            db_tools.insert_preset(
                7, 4, 'default_preset', NOW, is_default=True,
            ),
            _insert_version(10, 7, NOW, stops_at=NOW + WEEK),
        ]
        cursor.execute(';'.join(queries))

    # check single priority relation intersection
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.insert_priority_relation(constants.MSK, 0, True),
        )

    # check default preset without relations invariant
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_preset_relation(constants.MSK, 0))
    # non-default preset can have many different relations
    cursor.execute(db_tools.insert_preset_relation(constants.SPB, 1))

    # check different presets intersection for one priority
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_preset_relation(constants.MSK, 2))
    # but preset from another priority can relate to this agglomeration
    cursor.execute(db_tools.insert_preset_relation(constants.MSK, 4))

    # correct version stops_at update
    cursor.execute(
        db_tools.update_version_start_stop_time(3, stops_at=NOW + WEEK),
    )
    # test incorrect version update
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.update_version_start_stop_time(0, stops_at=NOW + WEEK),
        )
    # test stops_at less than starts_at
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.update_version_start_stop_time(0, stops_at=NOW - WEEK),
        )
    # test starts_at less than created_at
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.update_version_start_stop_time(0, starts_at=NOW - WEEK),
        )
    # test no infinite version
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.update_version_start_stop_time(5, stops_at=NOW + WEEK),
        )
    cursor.execute(
        db_tools.update_version_start_stop_time(0, None, NOW + HOUR),
    )

    # test unique preset name for one priority
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_preset(7, 0, 'preset0', NOW))

    # test priorities which can contain activity rules

    activity_queries = [
        db_tools.insert_priority(
            4, 'activity', True, 'tk', can_contain_activity_rule=True,
        ),
        db_tools.insert_preset(7, 4, 'default_preset', NOW, is_default=True),
        _insert_version(10, 7, NOW),
    ]
    cursor.execute(';'.join(activity_queries))
    with pytest.raises(psycopg2.DatabaseError):
        second_priority_queries = [
            db_tools.insert_priority(
                5,
                'second_activity_rule',
                True,
                'tk',
                can_contain_activity_rule=True,
            ),
            db_tools.insert_preset(
                8, 5, 'default_preset', NOW, is_default=True,
            ),
            _insert_version(11, 8, NOW),
        ]
        cursor.execute(';'.join(second_priority_queries))

    # check constraint unique(name, priority_id)
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            db_tools.insert_experiment(4, 0, 'first_exp', NOW, None),
        )

    # check experiments agglomeration relation
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_experiment_relation(constants.MSK, 1))
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(db_tools.insert_experiment_relation(constants.TULA, 0))

    # insert new correct experiments relations
    cursor.execute(db_tools.insert_experiment_relation(constants.TULA, 3))
    cursor.execute(db_tools.insert_experiment_relation('br_russia', 0))
    cursor.execute(
        ';'.join(
            [
                db_tools.insert_experiment(
                    4, 0, 'new_exp', NOW, 'just new exp',
                ),
                db_tools.insert_experiment_relation(constants.BR_ROOT, 4),
            ],
        ),
    )
