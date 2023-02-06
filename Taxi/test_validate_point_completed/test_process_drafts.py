import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/old-flow/v1/validation/point-visited'


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low'], 'unlock_delay_s': 100},
        'resurrect': {},
    },
)
@pytest.mark.now('2022-02-14T12:00:00+0000')
async def test_handler(taxi_scooters_ops, pgsql, stq):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'point_id': 'point_id_1',
                    'cargo_point_id': 'cargo_point_id_scooter_1',
                    'type': 'scooter',
                    'status': 'arrived',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'job_id_1',
                            'status': 'performing',
                            'type': 'do_nothing',
                            'typed_extra': {},
                        },
                        {
                            'job_id': 'job_id_2',
                            'status': 'failed',
                            'type': 'do_nothing',
                            'typed_extra': {},
                        },
                    ],
                },
            ],
        },
    )

    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_id_1',
            'type': 'recharge',
            'status': 'actual',
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_1',
            'job_id': 'job_id_1',
            'typed_extra': {'vehicle_id': 'vehicle_id_1'},
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_id_2',
            'type': 'resurrect',
            'status': 'actual',
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_1',
            'job_id': 'job_id_2',
            'typed_extra': {'vehicle_id': 'vehicle_id_1'},
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert resp.status == 200

    assert (
        db_utils.get_draft(
            pgsql,
            'draft_id_1',
            fields=['mission_id', 'point_id', 'job_id', 'status'],
        )
        == {
            'status': 'processed',
            'mission_id': 'mission_id_1',
            'point_id': 'point_id_1',
            'job_id': 'job_id_1',
        }
    )
    assert (
        db_utils.get_draft(
            pgsql,
            'draft_id_2',
            fields=['mission_id', 'point_id', 'job_id', 'status'],
        )
        == {
            'status': 'actual',
            'mission_id': None,
            'point_id': None,
            'job_id': None,
        }
    )

    assert stq.scooters_ops_remove_tags.times_called == 1
    utils.assert_partial_diff(
        stq.scooters_ops_remove_tags.next_call(),
        {
            'kwargs': {'tags': ['battery_low'], 'vehicle_id': 'vehicle_id_1'},
            'eta': utils.parse_timestring_aware(
                '2022-02-14T12:01:40+0000',
            ).replace(tzinfo=None),
        },
    )
