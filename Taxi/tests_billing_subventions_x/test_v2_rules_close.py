import datetime

import pytest

MOCK_NOW = '2020-07-21T00:00:00+03:00'


@pytest.mark.parametrize(
    'rule_ids, close_at, expected_draft',
    [
        (
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            '2020-08-01T00:00:00+03:00',
            {
                'creator': 'me',
                'draft_id': '12345',
                'tickets': 'TAXIRATE-1,TAXIRATE-2',
                'approved_at': datetime.datetime.fromisoformat(MOCK_NOW),
                'approvers': 'he,she',
                'spec': {
                    'rule_ids': ['2abf062a-b607-11ea-998e-07e60204cbcf'],
                    'close_at': '2020-07-31T21:00:00+00:00',
                },
                'state': 'APPROVED',
            },
        ),
        (
            ['2abf062a-b607-11ea-998e-07e60204cbdf'],
            '2020-08-01T00:00:00+03:00',
            {
                'creator': 'me',
                'draft_id': '12345',
                'tickets': 'TAXIRATE-1,TAXIRATE-2',
                'approved_at': datetime.datetime.fromisoformat(MOCK_NOW),
                'approvers': 'he,she',
                'spec': {
                    'rule_ids': ['2abf062a-b607-11ea-998e-07e60204cbdf'],
                    'close_at': '2020-07-31T21:00:00+00:00',
                },
                'state': 'APPROVED',
            },
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_close_saves_draft_info(
        rule_ids, close_at, expected_draft, taxi_billing_subventions_x, pgsql,
):
    query = make_query(rule_ids=rule_ids, close_at=close_at)
    await _make_request(taxi_billing_subventions_x, query)
    _assert_draft_created(pgsql, expected_draft)


def _assert_draft_created(pgsql, expected_draft):
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
       SELECT
        internal_draft_id,
        spec,
        created_at,
        creator,
        draft_id,
        tickets,
        approvers,
        approved_at,
        state
      FROM subventions.draft_spec WHERE draft_id = %s;
    """
    cursor.execute(sql, (expected_draft['draft_id'],))
    rows = cursor.fetchall()
    fields = [column.name for column in cursor.description]
    assert len(rows) == 1
    draft = dict(zip(fields, rows[0]))
    assert draft.pop('created_at')
    assert draft.pop('internal_draft_id')
    assert draft == expected_draft


@pytest.mark.parametrize(
    'rule_ids, close_at, expected_draft',
    [
        (
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            '2020-08-01T00:00:00+03:00',
            {
                'rule_id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'new_ends_at': datetime.datetime.fromisoformat(
                    '2020-07-31T21:00:00+00:00',
                ),
            },
        ),
        (
            ['2abf062a-b607-11ea-998e-07e60204cbdf'],
            '2020-08-01T00:00:00+03:00',
            {
                'rule_id': '2abf062a-b607-11ea-998e-07e60204cbdf',
                'new_ends_at': datetime.datetime.fromisoformat(
                    '2020-07-31T21:00:00+00:00',
                ),
            },
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_close_saves_drafted_rules(
        rule_ids, close_at, expected_draft, taxi_billing_subventions_x, pgsql,
):
    query = make_query(rule_ids=rule_ids, close_at=close_at)
    await _make_request(taxi_billing_subventions_x, query)
    _assert_drafted_rules_created(pgsql, expected_draft)


def _assert_drafted_rules_created(pgsql, expected_draft):
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
       SELECT
        rule_id,
        new_ends_at
      FROM subventions.draft_rules_to_close;
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    fields = [column.name for column in cursor.description]
    assert len(rows) == 1
    draft = dict(zip(fields, rows[0]))
    assert draft == expected_draft


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'rule_ids, close_at, rule_ends',
    [
        (
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            '2020-08-01T00:00:00+03:00',
            [
                (
                    '2abf062a-b607-11ea-998e-07e60204cbcf',
                    '2020-07-31T21:00:00+00:00',
                ),
                (
                    'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                    '2020-08-31T21:00:00+00:00',
                ),
            ],
        ),
        (
            ['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
            '2020-08-01T00:00:00+03:00',
            [
                (
                    '2abf062a-b607-11ea-998e-07e60204cbcf',
                    '2020-09-01T00:00:00+03:00',
                ),
                (
                    'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
                    '2020-07-31T21:00:00+00:00',
                ),
            ],
        ),
        (  # close earlier than starts_at
            ['68af85d6-4cdb-4de4-9bf7-d9cf02e1f990'],
            '2020-07-25T00:00:00+03:00',
            [
                (
                    '68af85d6-4cdb-4de4-9bf7-d9cf02e1f990',
                    '2020-08-01T00:00:00+03:00',
                ),
            ],
        ),
    ],
)
async def test_v2_rules_close_update_ends_at_for_demanded_rules(
        rule_ids, close_at, rule_ends, taxi_billing_subventions_x, pgsql,
):
    query = make_query(rule_ids=rule_ids, close_at=close_at)
    await _make_request(taxi_billing_subventions_x, query)
    for (rule_id, ends_at) in rule_ends:
        expected = datetime.datetime.fromisoformat(ends_at)
        assert _select_ends_at(pgsql, rule_id) == expected


def _select_ends_at(pgsql, rule_id):
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
        SELECT ends_at FROM subventions.rule
        WHERE rule_id = %(rule_id)s
    """
    cursor.execute(sql, {'rule_id': rule_id})
    return cursor.fetchone()[0]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'rule_ids, close_at, updated_at, changes',
    [
        (
            ['2abf062a-b607-11ea-998e-07e60204cbcf'],
            '2020-08-01T00:00:00+03:00',
            datetime.datetime.fromisoformat('2020-05-22T18:30:00+00:00'),
            [
                ('2abf062a-b607-11ea-998e-07e60204cbcf', True),
                ('cf730f12-c02b-11ea-acc8-ab6ac87f7711', False),
            ],
        ),
        (
            ['2abf062a-b607-11ea-998e-07e60204cbdf'],
            '2020-08-01T00:00:00+03:00',
            datetime.datetime.fromisoformat('2020-05-22T18:30:00+00:00'),
            [
                ('2abf062a-b607-11ea-998e-07e60204cbdf', True),
                ('cf730f12-c02b-11ea-acc8-ab6ac87f7721', False),
            ],
        ),
    ],
)
async def test_v2_rules_close_update_updated_at_for_demanded_rules(
        rule_ids,
        close_at,
        changes,
        updated_at,
        taxi_billing_subventions_x,
        pgsql,
):
    query = make_query(rule_ids=rule_ids, close_at=close_at)
    await _make_request(taxi_billing_subventions_x, query)
    for (rule_id, has_changed) in changes:
        assert (
            _select_updated_at(pgsql, rule_id) != updated_at
        ) is has_changed


def _select_updated_at(pgsql, rule_id):
    cursor = pgsql['billing_subventions'].cursor()
    sql = f"""
        SELECT updated_at FROM subventions.rule
        WHERE rule_id = %(rule_id)s
    """
    cursor.execute(sql, {'rule_id': rule_id})
    return cursor.fetchone()[0]


@pytest.mark.parametrize(
    'rule_id, close_at, last_log',
    [
        (
            '2abf062a-b607-11ea-998e-07e60204cbcf',
            '2020-08-01T00:00:00+03:00',
            {
                'row_id': 1,
                'rule_id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'draft_id': '12345',
                'initiator': 'me',
                'description': 'Close rule at 2020-07-31T21:00:00+0000',
            },
        ),
        (
            'cf730f12-c02b-11ea-acc8-ab6ac87f7721',
            '2020-08-01T00:00:00+03:00',
            {
                'row_id': 1,
                'rule_id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7721',
                'draft_id': '12345',
                'initiator': 'me',
                'description': 'Close rule at 2020-07-31T21:00:00+0000',
            },
        ),
        (  # close earlier than starts_at
            '68af85d6-4cdb-4de4-9bf7-d9cf02e1f990',
            '2020-07-25T00:00:00+03:00',
            {
                'row_id': 1,
                'rule_id': '68af85d6-4cdb-4de4-9bf7-d9cf02e1f990',
                'draft_id': '12345',
                'initiator': 'me',
                'description': 'Close rule at 2020-07-31T21:00:00+0000',
            },
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_close_logs_ends_at_changed(
        rule_id, close_at, last_log, taxi_billing_subventions_x, pgsql,
):
    query = make_query(rule_ids=[rule_id], close_at=close_at)
    await _make_request(taxi_billing_subventions_x, query)
    log = _get_log_for_rule(pgsql, rule_id)
    log.pop('event_at')
    assert log == last_log


def _get_log_for_rule(pgsql, rule_id):
    cursor = pgsql['billing_subventions'].cursor()
    sql = """
        SELECT * FROM subventions.rule_change_log
        WHERE rule_id = %s"""
    cursor.execute(sql, (rule_id,))
    fields = [column.name for column in cursor.description]
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(fields, rows[0]))


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'rule_id',
    (
        '2abf062a-b607-11ea-998e-07e60204cbcf',
        '0e694758-917e-11eb-b4e0-93732786c44f',
        'cf730f12-c02b-11ea-acc8-ab6ac87f7721',
    ),
)
async def test_v2_rules_close_fails_when_too_late(
        taxi_billing_subventions_x, rule_id,
):
    query = make_query(rule_ids=[rule_id], close_at=MOCK_NOW)
    data = await _make_request(taxi_billing_subventions_x, query, 400)
    assert data == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'Forbidden to close rules with a date in the past',
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'rules',
    (
        # single_ride
        ['2abf062a-b607-11ea-998e-07e60204cbcf'],
        # goals
        [
            '0e694758-917e-11eb-b4e0-93732786c44f',
            '4327ef77-2294-4bbf-847f-83a654a1c72d',
        ],
        # single_ontop
        [
            '2abf062a-b607-11ea-998e-07e60204cbdf',
            'cf730f12-c02b-11ea-acc8-ab6ac87f7721',
        ],
    ),
)
async def test_v2_rules_close_fails_when_moving_to_future(
        taxi_billing_subventions_x, rules,
):
    query = make_query(rule_ids=rules, close_at='2020-09-30T21:00:00+00:00')
    data = await _make_request(taxi_billing_subventions_x, query, 400)
    assert data == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'Forbidden to move the ending date to the future',
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_close_fails_when_new_period_is_not_multiple_of_window(
        taxi_billing_subventions_x,
):
    query = make_query(
        rule_ids=[
            '0e694758-917e-11eb-b4e0-93732786c44f',
            '4327ef77-2294-4bbf-847f-83a654a1c72d',
        ],
        close_at='2020-08-29T21:00:00+00:00',
    )
    data = await _make_request(taxi_billing_subventions_x, query, 400)
    assert data == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            '0e694758-917e-11eb-b4e0-93732786c44f: new activity '
            'period (90) must be multiple of the window size (7)'
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_close_fails_when_not_all_goals_from_the_draft_closed(
        taxi_billing_subventions_x,
):
    query = make_query(
        rule_ids=['0e694758-917e-11eb-b4e0-93732786c44f'],
        close_at='2020-08-02T21:00:00+00:00',
    )
    data = await _make_request(taxi_billing_subventions_x, query, 400)
    assert data == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Goals created simultaneously by the same draft must '
            'be closed simultaneously'
        ),
    }


async def _make_request(taxi_billing_subventions_x, query, status_code=200):
    headers = {
        'X-YaTaxi-Draft-Author': 'me',
        'X-YaTaxi-Draft-Id': '12345',
        'X-YaTaxi-Draft-Approvals': 'he,she',
        'X-YaTaxi-Draft-Tickets': 'TAXIRATE-1,TAXIRATE-2',
    }
    response = await taxi_billing_subventions_x.post(
        '/v2/rules/close', query, headers=headers,
    )
    assert response.status_code == status_code, response.json()
    return response.json()


def make_query(rule_ids, close_at='2021-01-01T00:00:00'):
    return {'rule_ids': rule_ids, 'close_at': close_at}


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, a_single_ontop, create_rules):
    create_rules(
        a_single_ride(
            id='2abf062a-b607-11ea-998e-07e60204cbcf',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
        a_single_ride(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
        a_single_ride(
            id='68af85d6-4cdb-4de4-9bf7-d9cf02e1f990',
            start='2020-08-01T00:00:00+03:00',
            end='2020-08-31T00:00:00+03:00',
        ),
    )
    create_rules(
        a_goal(
            id='0e694758-917e-11eb-b4e0-93732786c44f',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-30T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
        a_goal(
            id='4327ef77-2294-4bbf-847f-83a654a1c72d',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-30T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
        draft_id='goal_draft_id',
    )
    create_rules(
        a_single_ontop(
            id='2abf062a-b607-11ea-998e-07e60204cbdf',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
        a_single_ontop(
            id='cf730f12-c02b-11ea-acc8-ab6ac87f7721',
            start='2020-05-31T21:00:00+00:00',
            end='2020-08-31T21:00:00+00:00',
            updated_at='2020-05-22T18:30:00+00:00',
        ),
    )
