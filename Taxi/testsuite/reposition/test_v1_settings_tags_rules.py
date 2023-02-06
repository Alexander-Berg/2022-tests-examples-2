from datetime import datetime
from datetime import timedelta

import pytest

from .reposition_select import select_named
from .reposition_select import select_table_named


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'sample_tags.sql',
        'mode_home.sql',
        'sample_bonus_usages_rules.sql',
    ],
)
def test_get_empty(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/tags/rules?tag_id=tag_without_rules',
    )
    assert response.status_code == 200
    assert response.json() == {'bonus_usages': {}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_tag_not_found(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/tags/rules?tag_id=unknown_tag',
    )
    assert response.status_code == 200
    assert response.json() == {'bonus_usages': {}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'sample_tags.sql',
        'mode_home.sql',
        'sample_bonus_usages_rules.sql',
    ],
)
def test_get(taxi_reposition):
    response = taxi_reposition.get(
        '/v1/settings/tags/rules?tag_id=tag_with_rules',
    )
    assert response.status_code == 200
    assert response.json() == {
        'bonus_usages': {
            'home': {'day_bonus_usages': 5, 'day_bonus_duration_limit': 30},
        },
    }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put_tag_not_found(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/rules?tag_id=unknown_tag',
        json={'bonus_usages': {}},
    )
    assert response.status_code == 200
    assert (
        select_table_named(
            'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
        )
        == []
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'sample_tags.sql',
        'mode_home.sql',
        'sample_bonus_usages_rules.sql',
    ],
)
def test_put_empty_does_delete(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/rules?tag_id=tag_with_rules', json={},
    )
    assert response.status_code == 200
    assert (
        select_table_named(
            'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
        )
        == []
    )


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['sample_tags.sql', 'mode_home.sql'])
def test_put(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/rules?tag_id=tag_without_rules',
        json={
            'bonus_usages': {
                'home': {
                    'day_bonus_usages': 5,
                    'week_bonus_usages': 10,
                    'day_bonus_duration_limit': 30,
                    'week_bonus_duration_limit': 60,
                },
            },
        },
    )
    assert response.status_code == 200
    assert (
        select_table_named(
            'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
        )
        == [
            {
                'tag_id': None,
                'tag_name': 'tag_without_rules',
                'mode_id': 1,
                'day_bonus_usages': 5,
                'week_bonus_usages': 10,
                'day_bonus_duration_limit': timedelta(minutes=30),
                'week_bonus_duration_limit': timedelta(minutes=60),
            },
        ]
    )

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': False,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'sample_tags.sql',
        'mode_home.sql',
        'sample_bonus_usages_rules.sql',
    ],
)
def test_put_override(taxi_reposition, pgsql):
    response = taxi_reposition.put(
        '/v1/settings/tags/rules?tag_id=tag_with_rules',
        json={
            'bonus_usages': {
                'home': {'day_bonus_usages': 7, 'week_bonus_usages': 10},
            },
        },
    )
    assert response.status_code == 200
    assert (
        select_table_named(
            'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
        )
        == [
            {
                'tag_id': None,
                'tag_name': 'tag_with_rules',
                'mode_id': 1,
                'day_bonus_usages': 7,
                'week_bonus_usages': 10,
                'day_bonus_duration_limit': None,
                'week_bonus_duration_limit': None,
            },
        ]
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_delete_unknown_tag(taxi_reposition):
    response = taxi_reposition.delete(
        '/v1/settings/tags/rules?tag_id=unknown_tag',
    )
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['sample_tags.sql', 'mode_home.sql'])
def test_delete_non_existent(taxi_reposition, pgsql):
    response = taxi_reposition.delete(
        '/v1/settings/tags/rules?tag_id=tag_without_rules',
    )
    assert response.status_code == 200

    rows = select_table_named(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )
    assert rows == []


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'sample_tags.sql',
        'mode_home.sql',
        'sample_bonus_usages_rules.sql',
    ],
)
def test_delete(taxi_reposition, pgsql):
    response = taxi_reposition.delete(
        '/v1/settings/tags/rules?tag_id=tag_with_rules',
    )
    assert response.status_code == 200
    assert (
        select_table_named(
            'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
        )
        == []
    )

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': False,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]
