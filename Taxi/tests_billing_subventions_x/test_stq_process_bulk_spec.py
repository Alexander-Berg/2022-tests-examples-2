import pytest

from tests_billing_subventions_x import dbhelpers

SINGLE_RIDES_DRAFT = '072c6866-a3a4-11eb-aaa9-13ca81d72459'
PERSONAL_GOALS_DRAFT = 'e12d920f0a0839f3743b38ffe28747cd'
MOCK_NOW = '2021-04-30T19:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals.yaml'],
)
@pytest.mark.parametrize(
    'internal_draft_id,expected_json',
    (
        (PERSONAL_GOALS_DRAFT, 'expected_specs.json'),
        (SINGLE_RIDES_DRAFT, 'expected_specs_single_ride.json'),
    ),
)
async def test_stq_process_bulk_spec_creates_subdrafts(
        yt_apply,
        stq_runner,
        pgsql,
        load_json,
        internal_draft_id,
        expected_json,
):
    await _run(stq_runner, internal_draft_id)
    subdrafts = dbhelpers.select_subdrafts(pgsql, internal_draft_id)
    assert _fix_schedule_refs(subdrafts) == load_json(expected_json)


def _fix_schedule_refs(subdrafts):
    for subdraft in subdrafts:
        assert subdraft['spec']['rule'].pop('schedule_ref')
        subdraft['spec']['rule']['schedule_ref'] = '_'.join(
            ['schedule_ref', subdraft['spec_ref']],
        )
    return subdrafts


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals.yaml'],
)
@pytest.mark.parametrize(
    'internal_draft_id,expected_json',
    (
        (PERSONAL_GOALS_DRAFT, 'expected_specs.json'),
        (SINGLE_RIDES_DRAFT, 'expected_specs_single_ride.json'),
    ),
)
async def test_stq_process_bulk_spec_run_twice_is_safe(
        yt_apply,
        stq_runner,
        pgsql,
        load_json,
        internal_draft_id,
        expected_json,
):
    await _run(stq_runner, internal_draft_id)
    await _run(stq_runner, internal_draft_id)
    subdrafts = dbhelpers.select_subdrafts(pgsql, internal_draft_id)
    assert _fix_schedule_refs(subdrafts) == load_json(expected_json)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals.yaml'],
)
@pytest.mark.parametrize(
    'internal_draft_id', (PERSONAL_GOALS_DRAFT, SINGLE_RIDES_DRAFT),
)
async def test_stq_process_bulk_spec_start_generating_task(
        yt_apply, stq_runner, stq, internal_draft_id,
):
    await _run(stq_runner, internal_draft_id)
    queue = stq.billing_subventions_x_generate_rule_drafts
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == internal_draft_id
    assert task['kwargs']['internal_draft_id'] == internal_draft_id
    assert 'subdrafts' not in task['kwargs']


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals_broken.yaml'],
)
async def test_stq_process_bulk_spec_creates_subdrafts_even_totally_broken(
        yt_apply, stq_runner, pgsql,
):
    await _run(stq_runner, PERSONAL_GOALS_DRAFT)
    subdrafts = dbhelpers.select_subdrafts(pgsql, PERSONAL_GOALS_DRAFT)
    assert [subdraft['error'] for subdraft in subdrafts] == [
        'got nullptr_t instead of int64_t',
        (
            'Value of \'rule.counters.schedule\': incorrect size, '
            'must be 1 (limit) <= 0 (value)'
        ),
        'Activity period (7) must be multiple of the window size (3)',
    ]


@pytest.mark.now('2021-04-30T23:00:00+00:00')
async def test_stq_process_bulk_spec_creates_broken_subdrafs_single_ride(
        stq_runner, pgsql,
):
    await _run(stq_runner, SINGLE_RIDES_DRAFT)
    subdrafts = dbhelpers.select_subdrafts(pgsql, SINGLE_RIDES_DRAFT)
    msg = (
        'Rules\' start \'2021-04-30T21:00:00+0000\' must be greater than '
        '\'2021-04-30T23:00:00+0000\' + 1 hours'
    )
    assert [subdraft['error'] for subdraft in subdrafts] == [msg, msg]


@pytest.mark.now('2021-04-30T23:00:00+00:00')
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals_broken.yaml'],
)
@pytest.mark.parametrize(
    'internal_draft_id', (PERSONAL_GOALS_DRAFT, SINGLE_RIDES_DRAFT),
)
async def test_stq_process_bulk_spec_marks_broken_specs_as_completed(
        yt_apply, stq_runner, pgsql, internal_draft_id,
):
    await _run(stq_runner, internal_draft_id)
    subdrafts = dbhelpers.select_subdrafts(pgsql, internal_draft_id)
    for subdraft in subdrafts:
        assert subdraft['completed'] is True, subdraft


async def _run(stq_runner, internal_draft_id):
    await stq_runner.billing_subventions_x_process_bulk_spec.call(
        task_id='id', kwargs={'internal_draft_id': internal_draft_id},
    )


@pytest.fixture(autouse=True)
def _fill_db(create_drafts, a_draft, load_json):
    create_drafts(
        a_draft(
            internal_draft_id=PERSONAL_GOALS_DRAFT,
            spec={
                'budget': {
                    'weekly': '1000',
                    'rolling': False,
                    'threshold': 100,
                    'weekly_validation': False,
                    'daily_validation': False,
                },
                'currency': 'RUB',
                'end': '2021-06-07T21:00:00+00:00',
                'start': '2021-05-31T21:00:00+00:00',
                'path': '//path/to/yt/table',
            },
        ),
        a_draft(
            internal_draft_id=SINGLE_RIDES_DRAFT,
            spec=load_json('bulk_single_ride_spec.json'),
        ),
    )
