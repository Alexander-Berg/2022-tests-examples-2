from datetime import timedelta
import json

import pytest

from .reposition_select import select_table


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_empty(taxi_reposition):
    response = taxi_reposition.get('/v2/settings/usage_rules')
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.nofilldb()
@pytest.mark.parametrize('limitation_type', ['count', 'duration_limit_sum'])
def test_get(taxi_reposition, pgsql, load, limitation_type):
    queries = [
        load('mode_home.sql'),
        load('usage_rules_home_' + limitation_type + '.sql'),
    ]
    pgsql['reposition'].apply_queries(queries)

    response = taxi_reposition.get('/v2/settings/usage_rules')
    assert response.status_code == 200

    if limitation_type == 'count':
        assert response.json() == {
            'home': {
                'change_interval': 4,
                'usage_limit': {
                    'limit_by': 'session_count',
                    'daily_usage_count': 2,
                },
            },
        }
    elif limitation_type == 'duration_limit_sum':
        assert response.json() == {
            'home': {
                'change_interval': 4,
                'usage_limit': {
                    'limit_by': 'session_duration_limit_sum',
                    'daily_sum_limit': 120,
                    'weekly_sum_limit': 240,
                },
            },
        }


@pytest.mark.nofilldb()
@pytest.mark.parametrize('limitation_type', ['count', 'duration_limit_sum'])
def test_get_with_tags(taxi_reposition, pgsql, load, limitation_type):
    queries = [
        load('mode_home.sql'),
        load('tags_bonus_usages.sql'),
        load('usage_rules_home_' + limitation_type + '.sql'),
    ]
    pgsql['reposition'].apply_queries(queries)

    response = taxi_reposition.get('/v2/settings/usage_rules')
    assert response.status_code == 200

    if limitation_type == 'count':
        assert response.json() == {
            'home': {
                'change_interval': 4,
                'usage_limit': {
                    'limit_by': 'session_count',
                    'daily_usage_count': 2,
                },
                'bonus_usages': {
                    'selfemployed': {
                        'limit_by': 'session_count',
                        'daily_bonus_usages': 3,
                    },
                    'great_driver': {
                        'limit_by': 'session_duration_limit_sum',
                        'daily_bonus_sum_limit': 60,
                        'weekly_bonus_sum_limit': 180,
                    },
                },
            },
        }
    elif limitation_type == 'duration_limit_sum':
        assert response.json() == {
            'home': {
                'change_interval': 4,
                'usage_limit': {
                    'limit_by': 'session_duration_limit_sum',
                    'daily_sum_limit': 120,
                    'weekly_sum_limit': 240,
                },
                'bonus_usages': {
                    'selfemployed': {
                        'limit_by': 'session_count',
                        'daily_bonus_usages': 3,
                    },
                    'great_driver': {
                        'limit_by': 'session_duration_limit_sum',
                        'daily_bonus_sum_limit': 60,
                        'weekly_bonus_sum_limit': 180,
                    },
                },
            },
        }


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_put_mode_not_found(taxi_reposition):
    response = taxi_reposition.put(
        '/v2/settings/usage_rules?mode=home',
        json={
            'change_interval': 1,
            'usage_limit': {
                'limit_by': 'session_count',
                'daily_usage_count': 1,
                'weekly_usage_count': 5,
            },
        },
    )
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.parametrize('daily_usages', [2, None])
@pytest.mark.parametrize('weekly_usages', [6, None])
@pytest.mark.parametrize('change_interval', [5, None])
@pytest.mark.pgsql('reposition', files=['mode_crazy.sql'])
def test_check_absent_keys(
        taxi_reposition, daily_usages, weekly_usages, change_interval,
):
    daily_usages_errors = {
        'reposition.crazy.error.day_usages_exceeded',
        'reposition.crazy.error.day_duration_limit_exceeded',
        'reposition.crazy.limits.day.remains',
        'reposition.crazy.limits.day.duration_remains',
        'reposition.crazy.limits.day.title',
        'reposition.crazy.text_day_limit',
        'reposition.crazy.text_day_duration_limit',
    }
    weekly_usages_errors = {
        'reposition.crazy.error.week_usages_exceeded',
        'reposition.crazy.error.week_duration_limit_exceeded',
        'reposition.crazy.limits.week.remains',
        'reposition.crazy.limits.week.duration_remains',
        'reposition.crazy.limits.week.title',
        'reposition.crazy.text_week_limit',
        'reposition.crazy.text_week_duration_limit',
    }
    change_interval_errors = {
        'reposition.crazy.messages.change_alert_title',
        'reposition.crazy.limits.next_change_date',
        'reposition.crazy.limits.next_change_date_title',
    }
    change_alert = {'reposition.crazy.messages.change_alert'}

    data = {
        'change_interval': change_interval,
        'usage_limit': {
            'limit_by': 'session_count',
            'daily_usage_count': daily_usages,
            'weekly_usage_count': weekly_usages,
        },
    }

    response = taxi_reposition.put(
        '/v2/settings/usage_rules?mode=crazy', json=data,
    )

    if (
            daily_usages is None
            and weekly_usages is None
            and change_interval is None
    ):
        assert response.status_code == 200
        return

    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert 'text' in data['error']
    lines = data['error']['text'].split('\n')
    assert lines[0] == 'tanker key errors:'
    errors = {}
    for line in lines[1:]:
        spl = line.split(':')
        assert len(spl) == 2
        error_type, keys = map(lambda x: x.strip(), spl)
        errors[error_type] = set(map(lambda x: x.strip(), keys.split(',')))

    expected_errors = {}
    expected_errors['no tanker key'] = set()
    if daily_usages is not None:
        expected_errors['no tanker key'] |= daily_usages_errors
    if weekly_usages is not None:
        expected_errors['no tanker key'] |= weekly_usages_errors
    if change_interval is not None:
        expected_errors['no tanker key'] |= change_interval_errors
        expected_errors['unexpected arguments'] = change_alert

    assert errors == expected_errors


@pytest.mark.parametrize('day_from', [True, False])
@pytest.mark.parametrize('day_to', [True, False])
@pytest.mark.parametrize('week_from', [True, False])
@pytest.mark.parametrize('week_to', [True, False])
@pytest.mark.parametrize('interval_from', [True, False])
@pytest.mark.parametrize('interval_to', [True, False])
def test_put(
        taxi_reposition,
        pgsql,
        load,
        day_from,
        day_to,
        week_from,
        week_to,
        interval_from,
        interval_to,
):
    queries = [load('mode_home.sql')]
    if day_from or week_from or interval_from:
        queries.append(load('empty_usage_rules_home.sql'))
    if day_from:
        queries.append(load('set_day_limit.sql'))
    if week_from:
        queries.append(load('set_week_limit.sql'))
    if interval_from:
        queries.append(load('set_change_interval.sql'))
    pgsql['reposition'].apply_queries(queries)

    data = {}
    if day_to or week_to:
        data['usage_limit'] = {'limit_by': 'session_count'}
        if day_to:
            data['usage_limit']['daily_usage_count'] = 2
        if week_to:
            data['usage_limit']['weekly_usage_count'] = 7
    if interval_to:
        data['change_interval'] = 10

    response = taxi_reposition.put(
        '/v2/settings/usage_rules?mode=home', json=data,
    )
    assert response.status_code == 200

    rows = select_table('config.usage_rules', 'mode_id', pgsql['reposition'])
    assert len(rows) == 1
    assert rows[0][0] == 1
    assert rows[0][1] == (None if not day_to else 2)
    assert rows[0][2] == (None if not week_to else 7)
    assert rows[0][3] == (None if not interval_to else timedelta(10))


@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'tags_bonus_usages.sql',
        'empty_usage_rules_home.sql',
        'set_day_limit.sql',
    ],
)
@pytest.mark.parametrize('non_reposition_tag', [False, True])
@pytest.mark.parametrize('num_tags', [1, 2, 3])
def test_put_with_tags(
        taxi_reposition, pgsql, mockserver, non_reposition_tag, num_tags,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        if tag == 'random':
            return mockserver.make_response(
                json.dumps({'items': [], 'limit': 0, 'offset': 0}),
                content_type='application/json',
            )

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    data = {
        'usage_limit': {'limit_by': 'session_count', 'daily_usage_count': 2},
        'bonus_usages': {},
    }

    if non_reposition_tag:
        data['bonus_usages']['random'] = {
            'limit_by': 'session_count',
            'daily_bonus_usages': 1,
            'weekly_bonus_usages': 7,
        }

    if num_tags == 1 or num_tags == 3:
        data['bonus_usages']['selfemployed'] = {
            'limit_by': 'session_count',
            'daily_bonus_usages': 2,
            'weekly_bonus_usages': 5,
        }

    if num_tags == 2 or num_tags == 3:
        data['bonus_usages']['great_driver'] = {
            'limit_by': 'session_duration_limit_sum',
            'daily_bonus_sum_limit': 120,
            'weekly_bonus_sum_limit': 360,
        }

    response = taxi_reposition.put(
        '/v2/settings/usage_rules?mode=home', json=data,
    )

    if non_reposition_tag:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': 'Tag "random" doesn\'t belong to "reposition" topic',
            },
        }
        return

    assert response.status_code == 200

    rows = select_table(
        'config.tags_bonus_usages', 'mode_id, tag_name', pgsql['reposition'],
    )
    assert len(rows) == 3 if num_tags == 3 else 2
    if num_tags == 2 or num_tags == 3:
        assert rows[0][1:6] == (
            1,
            None,
            None,
            timedelta(minutes=120),
            timedelta(minutes=360),
        )

    if num_tags == 1 or num_tags == 3:
        row = rows[0] if num_tags == 1 else rows[1]
        assert row[1:6] == (1, 2, 5, None, None)


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_delete_mode_not_found(taxi_reposition):
    response = taxi_reposition.delete('/v2/settings/usage_rules?mode=home')
    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'Mode \'home\' not found'}}


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql'])
def test_delete_non_existent(taxi_reposition):
    response = taxi_reposition.delete('/v2/settings/usage_rules?mode=home')
    assert response.status_code == 200


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition', files=['mode_home.sql', 'usage_rules_home_count.sql'],
)
def test_delete(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v2/settings/usage_rules?mode=home')
    assert response.status_code == 200
    rows = select_table('config.usage_rules', 'mode_id', pgsql['reposition'])
    assert len(rows) == 0


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'usage_rules_home_count.sql',
        'tags_bonus_usages.sql',
    ],
)
def test_delete_with_tags(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v2/settings/usage_rules?mode=home')
    assert response.status_code == 200
    rows = select_table('config.usage_rules', 'mode_id', pgsql['reposition'])
    assert len(rows) == 0

    rows = select_table(
        'config.tags_bonus_usages', 'tag_name', pgsql['reposition'],
    )
    assert len(rows) == 1
    assert rows[0][1] == 3
